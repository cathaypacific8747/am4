AM4's data is malformed - we use these non-vanilla patches:

```sh
diff -Nar airports.csv airports.new.csv
```

```patch
556c556
< 565,Lydd,Lydd Airport,United Kingdom,Europe,EGMD,EGMD,50.95610046386719,0.9391670227050781,4938,43,54000,03/21
---
> 565,Lydd,Lydd Airport,United Kingdom,Europe,LYS,EGMD,50.95610046386719,0.9391670227050781,4938,43,54000,03/21
3171c3171
< 3241,Charlotte Amalie,Cyril E. King Airport,U.S. Virgin Islands,North America,TIST,TIST,18.337299346923828,-64.97339630126953,7000,90,6000,10/28
---
> 3241,Charlotte Amalie,Cyril E. King Airport,U.S. Virgin Islands,North America,STT,TIST,18.337299346923828,-64.97339630126953,7000,90,6000,10/28
```