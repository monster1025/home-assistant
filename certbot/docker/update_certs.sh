#!/bin/sh
while [ 1 ];
do
 certbot renew --agree-tos --standalone --preferred-challenges http-01
 sleep 1d
done
