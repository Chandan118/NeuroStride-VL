# VLCommand.msg
# Vision-Language Model Command

builtin_interfaces/Time stamp

string command                      # Natural language command
string action_type                  # Action type: "walk", "stop", "avoid"
float32 confidence                  # Confidence (0-1)

string scene_description            # Scene description
string[] objects                    # Detected objects
string[] hazards                    # Hazard list

string raw_response                 # Raw VLM response
