void setup() {
  Serial.begin(9600);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);

}

void loop() {

  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');

    if (data == "led1_on") {
      digitalWrite(5, 1);
    }
    if (data == "led1_off") {
      digitalWrite(5, 0);
    }


    if (data == "led2_on") {
      digitalWrite(6, 1);
    }
    if (data == "led2_off") {
      digitalWrite(6, 0);
    }

    if (data == "led3_on") {
      digitalWrite(7, 1);
    }
    if (data == "led3_off") {
      digitalWrite(7, 0);
    }

    if (data == "led4_on") {
      digitalWrite(8, 1);
    }
    if (data == "led4_off") {
      digitalWrite(8, 0);
    }

    if (data == "led5_on") {
      digitalWrite(9, 1);
    }
    if (data == "led5_off") {
      digitalWrite(9, 0);
    }

  }


}
