
//
// Generate a 9Hz square signal to trigger camera and lightning
//

// Arduino setup
void setup()
{
  // Output signal
  pinMode( 13, OUTPUT );
}

// Main loop
void loop()
{
  // High state (11ms)
  digitalWrite( 13, HIGH );
  delay( 11 );

  // Low state (100ms)
  digitalWrite( 13, LOW );
  delay( 100 );
}
