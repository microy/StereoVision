
//
// Generate a 9Hz signal to trigger camera and lightning
//

// Setup
int button = 7;
int trigger = 13;
int high_duration = 11;
int low_duration = 100;
boolean running = false;
int button_state;
int last_button_state = LOW;

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
