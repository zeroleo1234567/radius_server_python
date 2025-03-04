# 第三方库
from pyrad.packet import AuthPacket, AcctPacket, CoAPacket
from pyrad.dictionary import Dictionary
# 项目库
from .packet import PacketCode, init_packet_from_receive, init_packet_to_send
from .exception import AuthenticatorError
from controls.stat import NasStat
from loguru import logger as log
from .response import AuthResponse, AcctResponse


class AuthRequest(AuthPacket):
    """ receive access request """
    code = PacketCode.CODE_ACCESS_REQUEST

    def __init__(self, secret, dict: Dictionary, packet: bytes, socket, address):
        init_packet_from_receive(super(),
                                 code=self.code, id=0, secret=secret, authenticator=None, dict=dict, packet=packet)
        self.socket, self.address = socket, address
        # 报文提取
        # self['Service-Type'][0] 和 self['Service-Type'][1] 分别对应字典 dictionary.pyrad 里面 VALUE Service-Type Call-Check 10 的第1个和第2个值
        self.username = self['User-Name'][0]
        self.user_mac = self['Calling-Station-Id'][0]
        self.nas_name = self['NAS-Identifier'][0]
        self.nas_ip = self['NAS-IP-Address'][0]

        self.ssid = ''
        self.ap_mac = ''
        if 'Called-Station-Id' in self:
            self.ap_mac = self['Called-Station-Id'][0]    # 84-D9-31-7C-D6-00:WIFI-test
            if ':' in self.ap_mac:
                self.ap_mac, self.ssid = self.ap_mac.split(':', 1)

        self.auth_protocol = 'UNKNOWN-AUTH'

    def get_service_type(self) -> str:
        return self['Service-Type'][0]     # 2: Framed; 10: Call-Check;  https://datatracker.ietf.org/doc/html/rfc2865#page-31

    def reply_to(self, reply: AuthPacket):
        log.trace(f'reply: {reply}')
        if 'EAP-Message' in reply:
            reply.get_message_authenticator()   # 必须放在所有attribute设置好后, 发送前刷新 Message-Authenticator !!!
        self.socket.sendto(reply.ReplyPacket(), self.address)

    def create_reply(self, code) -> AuthResponse:
        NasStat.report_nas_ip(nas_ip=self.nas_ip, nas_name=self.nas_name)
        response = AuthResponse(id=self.id, secret=self.secret, authenticator=self.authenticator, dict=self.dict)
        response.code = code
        return response

    # @staticmethod
    # def get_message_authenticator(secret, buff):
    #     h = hmac.HMAC(key=secret)
    #     h.update(buff)
    #     return h.digest()

    def check_msg_authenticator(self):
        """
        报文内有Message-Authenticator, 则校验
        报文内没有Message-Authenticator:
            如果规则需要检验, 则返回False;
            如果规则不需要检验, 返回True. (使用secret对报文计算)
        """
        try:
            message_authenticator = self['Message-Authenticator'][0]
        except KeyError:
            return False
        expect_authenticator = self.get_message_authenticator()
        if expect_authenticator != message_authenticator:
            raise AuthenticatorError(f"Message-Authenticator mismatch. expect: {expect_authenticator.encode('hex')}, get: {message_authenticator}]")

        return


class AcctRequest(AcctPacket):
    """ receive accounting request """
    code = PacketCode.CODE_ACCOUNT_REQUEST

    def __init__(self, secret, dict, packet: bytes, socket, address):
        init_packet_from_receive(super(),
                                 code=self.code, id=0, secret=secret, authenticator=None, dict=dict, packet=packet)
        self.socket, self.address = socket, address
        # 报文提取
        self.username = self['User-Name'][0]
        self.user_mac = self['Calling-Station-Id'][0]
        self.nas_name = self['NAS-Identifier'][0]
        self.nas_ip = self['NAS-IP-Address'][0]
        self.iut = self["Acct-Status-Type"][0]   # I,U,T包. Start-1; Stop-2; Interim-Update-3; Accounting-On-7; Accounting-Off-8;
        self.auth_class = self.get("Class", (None, None))[0]

    def reply_to(self, reply: AcctPacket):
        log.trace(f'reply: {reply}')
        self.socket.sendto(reply.ReplyPacket(), self.address)

    def create_reply(self, code) -> AcctResponse:
        NasStat.report_nas_ip(nas_ip=self.nas_ip, nas_name=self.nas_name)
        response = AcctResponse(id=self.id, secret=self.secret, authenticator=self.authenticator, dict=self.dict)
        response.code = code
        return response


class RequestFactory(object):

    def __new__(cls, code, secret, dict, socket, address):
        if code == DmRequest.code:
            return DmRequest(secret=secret, dict=dict, socket=socket, address=address)
        if code == CoARequest.code:
            return CoARequest(secret=secret, dict=dict, socket=socket, address=address)

        raise Exception('')


class DmRequest(CoAPacket):
    """ send Disconnect Messages """
    code = PacketCode.CODE_DISCONNECT_REQUEST

    def __init__(self, secret, dict, socket, address):
        init_packet_to_send(super(), code=self.code, id=None, secret=secret, authenticator=None, dict=dict)
        self.socket, self.address = socket, address


class CoARequest(CoAPacket):
    """ send Change-of-Authorization (CoA) Messages """
    code = PacketCode.CODE_COA_REQUEST

    def __init__(self, secret, dict, socket, address):
        init_packet_to_send(super(), code=self.code, id=None, secret=secret, authenticator=None, dict=dict)
        self.socket, self.address = socket, address
