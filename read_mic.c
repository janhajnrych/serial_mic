int red = 7;
const int micPin  = A0;
int avg = 0;
const byte N = 16;
int values[N];
int delay_time_ms = 1000/120;
unsigned long time;

void setup() {
  pinMode(red, OUTPUT);
  pinMode(micPin, INPUT);
  Serial.println(F("Initialize System"));
  Serial.begin (9600);
    for (byte i=0; i<N; i++)
    values[i] = 0;
}

void readMicrophone( ) { /* function readMicrophone */
  for (byte i=0; i<N-1; i++)
    values[i+1] = values[i];
  values[0] = analogRead(micPin);
  avg = 0;
  for (byte i=0; i<N; i++)
    avg+=values[i];
  avg = avg/N;  
  if (values[0] - avg > 10)
    digitalWrite(red, HIGH);
  else
    digitalWrite(red, LOW);
  time = millis();
  
  Serial.print(time);
  Serial.print("/");
  Serial.println(values[0]);
}

void loop() {
  readMicrophone();
  //delay(delay_time_ms);
}
