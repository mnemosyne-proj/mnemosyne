#
# The idea of the SQL logger is to log events to an SQL database, with the same
# or similar layout as in the log analysis code: 
# http://ril.endoftheinternet.org/~jojkaart/mnemosyne_analysis_optimized.tar.gz
#
# Add the end of program, the SQL logged events should be dumped to log.txt as
# well, to be uploaded to the log analysis server.
#
# This should allow us to implement true undo. Also, together with code that
# imports the old logs into the database, this will allow us to show more
# statistics/graphs.
#
# There should be an SQLalchemy frontend to the database, so that it's easy for
# people to write their own queries.
#
# This is not necessarily 2.0 work, but could be postponed to later in the 2.x
# series.
