#include <Deneyap_Servo.h>      // Deneyap Servo kütüphanesi eklenmesi 

Servo servo1;                   // 1. servo motor için class tanımlanması
Servo servo2;                   // 2. servo motor için class tanımlanması
Servo servo3;                   // 3. servo motor için class tanımlanması 0 - 60
Servo servo4;                   // 3. servo motor için class tanımlanması
Servo servo5;                   // 3. servo motor için class tanımlanması 90 - 150

int d_time = 750;

void setup() {
  Serial.begin(9600);
  Serial.println("başladı");
  servo1.attach(D12);            // 1. servo motorun D3 pinin ve 0 kanal ayarlanması  /*attach(pin, channel=0, freq=50, resolution=12) olarak belirlenmiştir. Kullandığınız motora göre değiştirebilirsiniz */
  servo2.attach(D13,1);          // 2. servo motorun D4 pinin ve 1 kanal ayarlanması
  servo3.attach(D14,2);          // 3. servo motorun D5 pinin ve 3 kanal ayarlanması
  servo4.attach(A7,3);          // 3. servo motorun D5 pinin ve 3 kanal ayarlanması
  servo5.attach(D9,4);          // 3. servo motorun D5 pinin ve 3 kanal ayarlanması
}

void loop() {
  servo_test(servo2, 0, 180);
  //servo_toplu();
}


void servo_test(Servo s, int aci1, int aci2) {
  for (int i=aci1; i<aci2; i+=3){
    Serial.print("1 kiskac ->");
    Serial.println(i);
    s.write(i);             // 1. servo motorun milinin 30 derece dönmesi
    //delay(2);
  }
  s.write(aci1);
  delay(500);
}


void servo_toplu(){
  delay(d_time);
  Serial.println("1 omuz -> 0");
  servo1.write(0);             // 1. servo motorun milinin 30 derece dönmesi
  delay(d_time);
  Serial.println("1 omuz -> 180");
  servo1.write(180);             // 1. servo motorun milinin 30 derece dönmesi
  delay(d_time);

  Serial.println("2 dirsek -> 0");
  servo2.write(0);             // 2. servo motorun milinin 60 derece dönmesi
  delay(d_time);
  Serial.println("2 dirsek -> 180");
  servo2.write(180);             // 2. servo motorun milinin 60 derece dönmesi
  delay(d_time);

  Serial.println("3 kıskaç -> 0, 5 kıskaç 90");
  servo3.write(0);             // 3. servo motorun milinin 90 derece dönmesi
  servo5.write(60);             // 3. servo motorun milinin 90 derece dönmesi
  Serial.println("3 kıskaç -> 90, 5 kıskaç 0");
  delay(d_time);
  servo3.write(90);             // 3. servo motorun milinin 90 derece dönmesi
  servo5.write(150);             // 3. servo motorun milinin 90 derece dönmesi
  delay(d_time);

  Serial.println("4 çevre -> 0");
  servo4.write(0);             // 3. servo motorun milinin 90 derece dönmesi
  delay(d_time);
  Serial.println("4 çevre -> 180");
  servo4.write(180);             // 3. servo motorun milinin 90 derece dönmesi
  delay(d_time);

  delay(d_time);
  Serial.println("1 kiskac -> 0");
  servo5.write(0);             // 1. servo motorun milinin 30 derece dönmesi
  delay(d_time);
  Serial.println("1 kiskac -> 180");
  servo5.write(180);             // 1. servo motorun milinin 30 derece dönmesi
}

