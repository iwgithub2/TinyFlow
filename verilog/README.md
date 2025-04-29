To Convert from iscas85 format to a usable format:
```
read_verilog <verilog_source>
clean -purge 
write_verilog -sv -noattr > <verilog_dest>
```