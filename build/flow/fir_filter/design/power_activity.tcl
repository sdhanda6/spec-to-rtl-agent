# Auto-generated activity hook for OpenROAD final power reporting.
if { [info exists ::env(REPORT_POWER)] && $::env(REPORT_POWER) eq "0" } {
  puts "REPORT_POWER=0; skipping activity annotation"
} elseif { [info exists ::env(ACTIVITY_FILE)] && $::env(ACTIVITY_FILE) ne "" } {
  set activity_file $::env(ACTIVITY_FILE)
  if { [file exists $activity_file] } {
    set activity_scope ""
    if { [info exists ::env(ACTIVITY_SCOPE)] } {
      set activity_scope $::env(ACTIVITY_SCOPE)
    }
    if { $activity_scope ne "" } {
      puts "Reading activity VCD $activity_file with scope $activity_scope"
      if { [catch { read_vcd -scope $activity_scope $activity_file } activity_error] } {
        puts "Warning: scoped read_vcd failed: $activity_error"
        puts "Retrying activity VCD without an explicit scope"
        if { [catch { read_vcd $activity_file } fallback_error] } {
          puts "Warning: unscoped read_vcd failed: $fallback_error"
        }
      }
    } else {
      puts "Reading activity VCD $activity_file"
      if { [catch { read_vcd $activity_file } activity_error] } {
        puts "Warning: read_vcd failed: $activity_error"
      }
    }
  } else {
    puts "Warning: ACTIVITY_FILE $activity_file was not found; final power will use default activity"
  }
}
