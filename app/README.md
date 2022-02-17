# Automation Engine

This repository contains the code to automate 2-player python games. 

## How to Run

### Testing

```python engine.py```

When run independently, ```engine.py``` uses ```TestDBInterface``` to pull bot files from the ```/test``` directory. Only generates matches for the bots explicitly pulled via a call to ```handle_new_bot```. Add more calls of ```handle_new_bot``` if you want every possible match to happen. 

### Production

Something flask related... TBD
