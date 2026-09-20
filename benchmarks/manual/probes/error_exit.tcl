# Exercise a caught Tcl failure without depending on an unsupported JG command.
clear -all
if {[catch {error "ENVIRONMENT_EXPECTED_ERROR"} message]} {
  puts "ENVIRONMENT_ERROR_CAUGHT $message"
  exit 1
}
exit 2
