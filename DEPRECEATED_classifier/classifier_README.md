# Information for classifier

## more stack
due to the lack of enough stack from the standard config of gcc we compiled the c file using ``512 mb`` of stack. Depending on your os and/or compiler (version) this could be important

## csv
if you made the power and data csv files so that an EOL consits of solely LF or CR please comment out the line in ``classifier.c`` in the csv reader, that says COMMENT OUT!