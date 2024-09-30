import cv2
import math
import time
from cvzone.PoseModule import PoseDetector
import cvzone.HandTrackingModule as htm
import cvzone
from dk_connection import ImageReceiver, SocketServer

#SOL
# OMUZ = 12
# DIRSEK = 14
# BILEK = 16
# PARMAK = 22
# BEL = 24

#SAĞ
OMUZ = 11
DIRSEK = 13
BILEK = 15
PARMAK = 21
BEL = 23


class RobotArm:
    def __init__(self, target_width=1920, target_height=1080, source = "camera", detection_confidence=0.65, max_hands=1,):
        self.target_width = target_width
        self.target_height = target_height
        self.source = source

        self.restart_img = cv2.resize(cv2.imread("assets/restart.png", cv2.IMREAD_UNCHANGED), (50, 50))


        if source == "camera":
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, self.target_width)
            self.cap.set(4, self.target_height)
        else:
            self.sock_server = SocketServer()
            self.image_receiver = ImageReceiver(self.sock_server)

        self.detector = PoseDetector()
        self.hand_detector = htm.HandDetector(detectionCon=detection_confidence, maxHands=max_hands)
        self.lmList = []
        self.now = time.time()
        self.max_length = 1
        

    def get_img(self):
        img = None
        succes = None
        if self.source == "sock":
            img = self.image_receiver.get_image()
            succes = img is not None
        else:
            succes, img = self.cap.read()
        return succes, img
    
    def send_data(self, omuz_ang, dirsek_ang, bilek_ang, cevre_ang):
        self.sock_server.send_data(f"{omuz_ang:.2f},{dirsek_ang:.2f},{bilek_ang:.2f},{cevre_ang:.2f}")

    def draw_position(self, num: list, img):
        for l in num:
            cx, cy, cz = self.lmList[l]
            cv2.putText(img, str((cx, cy, cz)), (cx, cy),
                        cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), 2)

    def calculate_angle(self, A, B, C):
        # Vektörleri hesapla
        BA = (A[0] - B[0], A[1] - B[1])
        BC = (C[0] - B[0], C[1] - B[1])

        # Noktasal çarpımı hesapla
        dot_product = BA[0] * BC[0] + BA[1] * BC[1]

        # Uzunlukları hesapla
        length_BA = math.sqrt(BA[0] ** 2 + BA[1] ** 2)
        length_BC = math.sqrt(BC[0] ** 2 + BC[1] ** 2)

        # Açıyı hesapla
        cos_theta = dot_product / (length_BA * length_BC)
        theta = math.acos(cos_theta)

        # Çapraz çarpımı hesapla (yön kontrolü)
        cross_product = BA[0] * BC[1] - BA[1] * BC[0]

        # Açının yönünü belirle ve pozitif açı olarak döndür
        if cross_product < 0:
            theta = -theta

        # Radyanı dereceye çevir
        theta_degrees = math.degrees(theta)

        # Açının pozitif olup olmadığını kontrol et
        if theta_degrees < 0:
            theta_degrees += 360

        return 360 - theta_degrees


    def draw_angle(self, cord, img):
        angle = self.calculate_angle(
            self.lmList[cord[0]], self.lmList[cord[1]], self.lmList[cord[2]])
        angle = self.limit_value(angle)
        cx, cy, _ = self.lmList[cord[1]]
        cv2.putText(img, f"{angle:.2f}", (cx, cy + 30),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 100), 2)
        return angle
    
    def draw_angle2(self, cord, img):
        angle = self.calculate_angle(
            cord[0], cord[1], cord[2])
        angle = self.limit_value(angle)
        if angle > 90:
            angle = 180 - angle
        cx, cy = cord[2]
        cv2.putText(img, f"{angle:.2f}", (cx, cy + 30),
                    cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 100), 2)
        return angle


    def calculate_humerus_length(self):
        up = self.lmList[OMUZ]
        down = self.lmList[DIRSEK]
        length = abs(up[0] - down[0])
        if length > self.max_length:
            self.max_length = length

    def calculate_arm_angle(self,img):
        sing = 1 if self.lmList[DIRSEK][0] < self.lmList[OMUZ][0] else -1
        up = self.lmList[OMUZ]
        down = self.lmList[DIRSEK]
        length = abs(up[0] - down[0])
        angle = ((180 * length)/self.max_length)
        angle = (angle if angle <= 180 else angle - 180) * sing
        angle = self.limit_value(angle)
        cv2.putText(img, f"aci: {angle:.2f} - uzunluk: {length}", (120, 120),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 12, 100), 2)
        return angle
    
    def limit_value(self, value):
            value = abs(value)
            if value > 180:
                return value - 180
            else:
                return value

    def draw_restart(self, img: cv2.typing.MatLike) -> cv2.typing.MatLike:
        x,y,z = self.lmList[PARMAK]
        if self.target_width - 75 < x < self.target_width - 25 and self.target_height // 2 - 25 < y < self.target_height // 2 + 25:
            self.now = time.time()
            self.max_length = 1
            print("restart")
        return cvzone.overlayPNG(img, self.restart_img, [self.target_width - 75,  self.target_height //2])

    def draw_fingers(self, img, hands):
        bas, bilek, isaret = hands[0]["lmList"][4],hands[0]["lmList"][0], hands[0]["lmList"][8]
        # print(bas[0:2], bilek[0:2], isaret[0:2])
        cv2.line(img, bas[0:2], isaret[0:2], (255, 0, 0), 3)
        return self.draw_angle2((bas[0:2], bilek[0:2], isaret[0:2]), img)


    def main(self):
        while True:
            success, img = success, img = self.get_img()
            if not success:
                break
            img = cv2.flip(img, 1)
            img = cv2.resize(img, (self.target_width, self.target_height))

            img = self.detector.findPose(img)
            hands, img = self.hand_detector.findHands(img, flipType=True)
            


            self.lmList, bbinfo = self.detector.findPosition(img)

            if len(self.lmList) != 0:
                if time.time() - self.now < 1:
                    self.calculate_humerus_length()
                    print(self.max_length)
                else:
                    img = self.draw_restart(img)
                    self.draw_position([OMUZ, DIRSEK], img)
                    dirsek_ang = self.draw_angle((OMUZ, DIRSEK, BILEK), img)
                    omuz_ang = self.draw_angle((BEL, OMUZ, DIRSEK), img)
                    bilek_ang = self.draw_angle((DIRSEK, BILEK, PARMAK), img)
                    cevre_ang = self.calculate_arm_angle(img)
                    if hands:
                        bilek_ang = self.draw_fingers(img, hands)
                    if self.source == "sock":
                        self.send_data(bilek_ang=bilek_ang, cevre_ang=cevre_ang, 
                                    dirsek_ang=dirsek_ang, omuz_ang=omuz_ang)
                if self.max_length == 0:
                    self.max_length = 200


            cv2.imshow("Deneyap", img)
            if cv2.waitKey(5) & 0xFF == 27:
                print("çık")
                break

if __name__ == "__main__":
    ra = RobotArm(source="camera")
    ra.main()