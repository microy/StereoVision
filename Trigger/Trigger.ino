
//
// Generate a signal to trigger camera and lightning
//

// Setup
int button = 7;
int trigger = 13;
boolean running = false;
int button_state;
int last_button_state = LOW;

// 5 Hz
int high_duration = 10;
int low_duration = 190;

// 9 Hz
//int high_duration = 10;
//int low_duration = 101;

// Arduino setup
void setup() {
  // Input signal
  pinMode( button, INPUT );
  // Output signal
  pinMode( trigger, OUTPUT );
}

// Main loop
void loop() {
  // Start / Stop button
  button_state = digitalRead( button );
  if( button_state == HIGH && last_button_state == LOW ) {
    running = !running;
    delay( 50 );
  }
  last_button_state = button_state;
  // Trigger
  if( running ) {
    // High state
    digitalWrite( trigger, HIGH );
    delay( high_duration );
    // Low state
    digitalWrite( trigger, LOW );
    delay( low_duration );
  }
}
