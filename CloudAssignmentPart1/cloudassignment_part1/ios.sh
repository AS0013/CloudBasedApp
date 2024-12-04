# Remove the directory if it exists
rm -r -f build/cloudassignment_part1/iOS
# Execute the Briefcase commands
briefcase create iOS
briefcase build iOS
briefcase package iOS
briefcase run iOS -d "add your device id here"