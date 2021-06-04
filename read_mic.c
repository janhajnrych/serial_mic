int diode_pin_id = 7;
const int microphone_pin_id = A0;
int avg = 0;
const byte N = 16;
int values[N];
int delay_time_ms = 1000/120;
unsigned long time;

void setup() {
  pinMode(diode_pin_id, OUTPUT);
  pinMode(microphone_pin_id, INPUT);
  Serial.println(F("Initialize System"));
  Serial.begin (9600);
    for (byte i=0; i<N; i++)
    values[i] = 0;
}

void readMicrophone( ) { /* function readMicrophone */
  for (byte i=0; i<N-1; i++)
    values[i+1] = values[i];
  values[0] = analogRead(microphone_pin_id);
  avg = 0;
  for (byte i=0; i<N; i++)
    avg+=values[i];
  avg = avg/N;  
  if (values[0] - avg > 10)
    digitalWrite(diode_pin_id, HIGH);
  else
    digitalWrite(diode_pin_id, LOW);
  time = millis();
  
  Serial.print(time);
  Serial.print("/");
  Serial.println(values[0]);
}

void loop() {
  readMicrophone();
  delay(delay_time_ms);
}
