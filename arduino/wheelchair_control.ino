// Motor driver pin definitions
#define ENA 9   // Enable pin for Motor A
#define IN1 8   // Motor A input 1
#define IN2 7   // Motor A input 2
#define ENB 10  // Enable pin for Motor B
#define IN3 4   // Motor B input 1
#define IN4 5   // Motor B input 2

// Ultrasonic sensor pin definitions
#define TRIG 12  // Ultrasonic sensor trigger pin
#define ECHO 13  // Ultrasonic sensor echo pin

int speedValue = 150;  // Default motor speed (0-255)

void setup() {
  Serial.begin(9600);
  
  // Motor driver pin modes
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  
  // Ultrasonic sensor pin modes
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  
  // Stop motors initially
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  
  analogWrite(ENA, speedValue);
  analogWrite(ENB, speedValue);
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();
    
    if (command == 'F') {
      moveForward();
    } else if (command == 'L') {
      turnLeft();
    } else if (command == 'R') {
      turnRight();
    } else if (command == 'S') {
      stopWheelchair();
    } else if (command == 'G') {
      float distance = getUltrasonicDistance();
      Serial.println(distance);  // Send distance to Python
    }
  }
}

// Function to move forward
void moveForward() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

// Function to turn left
void turnLeft() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

// Function to turn right
void turnRight() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

// Function to stop
void stopWheelchair() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

// Function to get distance from ultrasonic sensor
float getUltrasonicDistance() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  
  long duration = pulseIn(ECHO, HIGH);
  float distance = (duration * 0.034) / 2;  // Convert to cm
  
  if (distance <= 0) {
    distance = 400;  // Default to max range if no valid reading
  }
  
  return distance;
}
