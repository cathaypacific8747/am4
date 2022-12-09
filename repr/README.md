weird issue occurs when pandas is also imported https://github.com/blue-yonder/turbodbc/issues/320
to replicate:
```
docker compose up
docker exec -it repr-client-1 bash
# pip3 install pandas
# python3
>>> import pandas
>>> import turbodbc
>>> con = turbodbc.connect(connection_string="DRIVER=MySQL ODBC 8.0 Unicode Driver;SERVER=mysql;USER=root;PASSWORD=root")
```
fails.

issue can possibly be mitigated by slowly downgrading the pandas version s.t. it is < arrow.
however the root cause of this error is still unclear and nondeterministic.