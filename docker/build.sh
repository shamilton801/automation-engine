# Run this to build the image used by the engine
# If running on windows, make sure you have wsl installed
#   and run "bash ./build.sh" inside powershell
docker build --no-cache -t python . 