# Remove the directory if it exists
if (Test-Path -Path "build/cloudassignment_part1/android") {
    Remove-Item -Path "build/cloudassignment_part1/android" -Recurse -Force
}

# Execute the Briefcase commands
briefcase create android
briefcase build android
briefcase package android
briefcase run android -d "add your device name here"
