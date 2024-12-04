# Remove the directory if it exists
rm -r -f build/cloudassignment_part1/macOS
rm -r -f build/cloudassignment_part1/ubuntu
rm -r -f build/cloudassignment_part1/linux
rm -r -f build/cloudassignment_part1/windows
# Execute the Briefcase commands
briefcase create
briefcase build
briefcase package --adhoc-sign
briefcase run