/*  RickRollCode

    AUTHOR: Rowan Packard
    rowanpackard@gmail.com

    DISCLAIMER: The song "Never Gonna Give You Up" by Rick Astley
    is not the creative property of the author. This code simply
    plays a Piezo buzzer rendition of the song.
*/

#define  a3f    208     // 208 Hz
#define  b3f    233     // 233 Hz
#define  b3     247     // 247 Hz
#define  c4     261     // 261 Hz MIDDLE C
#define  c4s    277     // 277 Hz
#define  e4f    311     // 311 Hz    
#define  f4     349     // 349 Hz 
#define  a4f    415     // 415 Hz  
#define  b4f    466     // 466 Hz 
#define  b4     493     // 493 Hz 
#define  c5     523     // 523 Hz 
#define  c5s    554     // 554 Hz
#define  e5f    622     // 622 Hz  
#define  f5     698     // 698 Hz 
#define  f5s    740     // 740 Hz
#define  a5f    831     // 831 Hz 

#define rest    -1

int piezo = 6; // Connect your piezo buzzer to this pin or change it to match your circuit!
int led = LED_BUILTIN; 

volatile int beatlength = 100; // determines tempo
float beatseparationconstant = 0.3;

int threshold;

int a; // part index
int b; // song index
int c; // lyric index

boolean flag;

// Parts 1 and 2 (Intro)

int song1_intro_melody[] =
{c5s, e5f, e5f, f5, a5f, f5s, f5, e5f, c5s, e5f, rest, a4f, a4f};

int song1_intro_rhythmn[] =
{6, 10, 6, 6, 1, 1, 1, 1, 6, 10, 4, 2, 10};

// Parts 3 or 5 (Verse 1)

int song1_verse1_melody[] =
{ rest, c4s, c4s, c4s, c4s, e4f, rest, c4, b3f, a3f,
  rest, b3f, b3f, c4, c4s, a3f, a4f, a4f, e4f,
  rest, b3f, b3f, c4, c4s, b3f, c4s, e4f, rest, c4, b3f, b3f, a3f,
  rest, b3f, b3f, c4, c4s, a3f, a3f, e4f, e4f, e4f, f4, e4f,
  c4s, e4f, f4, c4s, e4f, e4f, e4f, f4, e4f, a3f,
  rest, b3f, c4, c4s, a3f, rest, e4f, f4, e4f
};

int song1_verse1_rhythmn[] =
{ 2, 1, 1, 1, 1, 2, 1, 1, 1, 5,
  1, 1, 1, 1, 3, 1, 2, 1, 5,
  1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 3,
  1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 4,
  5, 1, 1, 1, 1, 1, 1, 1, 2, 2,
  2, 1, 1, 1, 3, 1, 1, 1, 3
};

const char* lyrics_verse1[] =
{ "We're ", "no ", "strangers ", "", "to ", "love ", "", "\r\n",
  "You ", "know ", "the ", "rules ", "and ", "so ", "do ", "I\r\n",
  "A ", "full ", "commitment's ", "", "", "what ", "I'm ", "thinking ", "", "of", "\r\n",
  "You ", "wouldn't ", "", "get ", "this ", "from ", "any ", "", "other ", "", "guy\r\n",
  "I ", "just ", "wanna ", "", "tell ", "you ", "how ", "I'm ", "feeling", "\r\n",
  "Gotta ", "", "make ", "you ", "understand", "", "\r\n"
};

// Parts 4 or 6 (Chorus)

int song1_chorus_melody[] =
{ b4f, b4f, a4f, a4f,
  f5, f5, e5f, b4f, b4f, a4f, a4f, e5f, e5f, c5s, c5, b4f,
  c5s, c5s, c5s, c5s,
  c5s, e5f, c5, b4f, a4f, a4f, a4f, e5f, c5s,
  b4f, b4f, a4f, a4f,
  f5, f5, e5f, b4f, b4f, a4f, a4f, a5f, c5, c5s, c5, b4f,
  c5s, c5s, c5s, c5s,
  c5s, e5f, c5, b4f, a4f, rest, a4f, e5f, c5s, rest
};

int song1_chorus_rhythmn[] =
{ 1, 1, 1, 1,
  3, 3, 6, 1, 1, 1, 1, 3, 3, 3, 1, 2,
  1, 1, 1, 1,
  3, 3, 3, 1, 2, 2, 2, 4, 8,
  1, 1, 1, 1,
  3, 3, 6, 1, 1, 1, 1, 3, 3, 3, 1, 2,
  1, 1, 1, 1,
  3, 3, 3, 1, 2, 2, 2, 4, 8, 4
};

const char* lyrics_chorus[] =
{ "Never ", "", "gonna ", "", "give ", "you ", "up\r\n",
  "Never ", "", "gonna ", "", "let ", "you ", "down", "", "\r\n",
  "Never ", "", "gonna ", "", "run ", "around ", "", "", "", "and ", "desert ", "", "you\r\n",
  "Never ", "", "gonna ", "", "make ", "you ", "cry\r\n",
  "Never ", "", "gonna ", "", "say ", "goodbye ", "", "", "\r\n",
  "Never ", "", "gonna ", "", "tell ", "a ", "lie ", "", "", "and ", "hurt ", "you\r\n"
};



void play() {
  int notelength;
  if (a == 1 || a == 2) {
    // intro
    notelength = beatlength * song1_intro_rhythmn[b];
    if (song1_intro_melody[b] > 0) {
      digitalWrite(led, HIGH);
      tone(piezo, song1_intro_melody[b], notelength);
    }
    b++;
    if (b >= sizeof(song1_intro_melody) / sizeof(int)) {
      a++;
      b = 0;
      c = 0;
    }
  }
  else if (a == 3 || a == 5) {
    // verse
    notelength = beatlength * 2 * song1_verse1_rhythmn[b];
    if (song1_verse1_melody[b] > 0) {
      digitalWrite(led, HIGH);
      Serial.print(lyrics_verse1[c]);
      tone(piezo, song1_verse1_melody[b], notelength);
      c++;
    }
    b++;
    if (b >= sizeof(song1_verse1_melody) / sizeof(int)) {
      a++;
      b = 0;
      c = 0;
    }
  }
  else if (a == 4 || a == 6) {
    // chorus
    notelength = beatlength * song1_chorus_rhythmn[b];
    if (song1_chorus_melody[b] > 0) {
      digitalWrite(led, HIGH);
      Serial.print(lyrics_chorus[c]);
      tone(piezo, song1_chorus_melody[b], notelength);
      c++;
    }
    b++;
    if (b >= sizeof(song1_chorus_melody) / sizeof(int)) {
      Serial.println("");
      a++;
      b = 0;
      c = 0;
    }
  }
  delay(notelength);
  noTone(piezo);
  digitalWrite(led, LOW);
  delay(notelength * beatseparationconstant);
  if (a == 7) { // loop back around to beginning of song
    a = 1;
  }
}


//--------------------------------------------------------------------------------------------------------


class color {
  public:

    int input_id;
    int output_id;

    int freq;
    int tone_pin;

    boolean pressed = false;
    boolean last_pressed;
    boolean button_pressed;

    color(int input, int output, int freqency,int tone_input) {
      input_id = input;
      output_id = output;
      freq = freqency;
      tone_pin = tone_input;
    }

    void turnOn() {
      digitalWrite(output_id, HIGH);
    };

    void turnOff() {
      digitalWrite(output_id, LOW);
    }

    void makesound(int duration){
      tone(tone_pin,freq,duration);
    }


    void on_wait(int wait_time) {

      turnOn();
      makesound(wait_time);
      delay(wait_time);
      turnOff();
      
    }


    void led_update() {
      delay(10);
      last_pressed = pressed;
      pressed = (digitalRead(input_id) == LOW);
      if ((last_pressed == false) && (pressed == true)) {
        button_pressed = true;
      } else {
        button_pressed = false;
      }
    }

    boolean is_pressed() {
      return button_pressed;
    }
};

class game {
  public:

    int input_list[100];
    int list_size = 0;
    int inputed_value;

    color yellow;
    color blue;
    color red;
    color green;
    public: color* color_list[4];

    game(color yellow_input, color blue_input, color red_input, color green_input)
      : yellow(yellow_input), blue(blue_input), red(red_input), green(green_input)
    {
      color_list[0] = &yellow;
      color_list[1] = &blue;
      color_list[2] = &red;
      color_list[3] = &green;
    }

    void game_update() {
      for (int i = 0; i < 4; i++) {
        color_list[i] -> led_update();
      }
    }

    int is_button_pressed() {
      for (int i = 0; i < 4; i++) {
        if (color_list[i] -> is_pressed()) {
          return i;
        }
      }

      return -1;
    }

    void add_random() {
      list_size++;
      input_list[list_size] = random(0, 4);
      Serial.println("input phase");
      
      for(int i = 0; i < list_size; i++)
      {
        Serial.print(input_list[i]);
      }
      Serial.println("");
    }

    void reset_array() {
      for (int i = 0; i < 100; i++) {
        input_list[i] = -1;
      }
      list_size = -1;
      add_random();
    }

    void output_phase() {
      Serial.println("output phase");
      add_random();
      for (int i = 0; i < list_size; i++) {
        color_list[input_list[i]] -> on_wait(500);
        delay(200);

      }

    }

    boolean input_phase() {
      for (int i = 0; i < list_size; i++) {
        boolean is_inputed = false;
        Serial.print("input phase");
        while (is_inputed == false) {
          
          game_update();
          inputed_value = is_button_pressed();
          
          if (inputed_value != -1) {
            is_inputed = true;
          }
        }

        Serial.print("chosen color is   ");
        Serial.println(inputed_value);
        Serial.print("actual color is   ");
        Serial.println(input_list[i]);

        color_list[inputed_value] -> on_wait(300);

        if (inputed_value != input_list[i]) {
          return false;
        }
      }

      return true;
    }

    void reset_phase() {
      reset_array();
    }

};



int yellow_led = 8;
int blue_led = 9;
int red_led = 10;
int green_led = 11;

int yellow_input = 2;
int blue_input = 3;
int red_input = 4;
int green_input = 5;

int yellow_freq = 400;
int blue_freq = 500;
int red_freq = 600;
int green_freq = 700;

int sound_pin = 6;

color yellow(yellow_input, yellow_led,yellow_freq,sound_pin);
color blue(blue_input, blue_led,blue_freq,sound_pin);
color red(red_input, red_led,red_freq,sound_pin);
color green(green_input, green_led,green_freq,sound_pin);
game actual_game(yellow, blue, red,green);



boolean game_started;


void setup() {
  // put your setup code here, to run once:

  a=4;
  b = 0;
  c = 0;

  pinMode(piezo, OUTPUT);
  pinMode(led, OUTPUT);

  digitalWrite(led, LOW);
  Serial.begin(9600);
  flag = true;

  game_started = false;

  pinMode(yellow_led, OUTPUT);
  pinMode(blue_led, OUTPUT);
  pinMode(red_led, OUTPUT);
  pinMode(green_led, OUTPUT);

  pinMode(yellow_input, INPUT_PULLUP);
  pinMode(blue_input, INPUT_PULLUP);
  pinMode(red_input, INPUT_PULLUP);
  pinMode(green_input, INPUT_PULLUP);

  Serial.begin(9600);
  randomSeed(analogRead(A3)*100);
}

void loop() {

  while (game_started == false) {
    
    actual_game.game_update();
    
    if(actual_game.is_button_pressed() != -1){
      game_started = true;
      yellow.on_wait(100);
      blue.on_wait(100);
      red.on_wait(100);
      green.on_wait(100);

      delay(500);

    }

  }
  
  Serial.println("starting");
  
  actual_game.output_phase();
  
  boolean success = actual_game.input_phase();

  delay(500);

  if (!success) {

        
    unsigned long end_time = millis() + 7000;
    
    while (millis()  < end_time) {
      int i = random(0, 4);
    
      actual_game.color_list[i]->turnOff();
      play();
      actual_game.color_list[i]->turnOn();
    }

    delay(200);
    a=4;
    b = 0;
    c = 0;

    
    
    actual_game.reset_phase();

    game_started = false;
  }
}
