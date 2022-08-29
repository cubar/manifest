## PostgreSQL backup procedure

The database backup procedure makes use of Linux Crontab to schedule jobs in the Manifest VM.
These jobs are scheduled to run every night and send the binaries of database dumps 
to an object storage in the Linode cloud. The dumps are encrypted in trasit and the key to
the encryption was shared using the key sharing system.

The database dump was done using the `pg_dump` command which is the official postgres command
to extract consistent database files and the `s3cmd` was used to send this file to the Linode
cloud. In addition, the backup extracted locally is removed from disk after being sent to Linode.

## Object storage lifecycle policy

In order to automatically remove old database dumps from the object storage we need to first
configure a lifecycle policy. The lifecycle policy is expressed in XML and versioned along
with this documentation.

The command used to create the policy is:

s3cmd setlifecycle lifecycle_policy.xml s3://example-bucket

Make sure to first bootstrap the `s3cmd` using this:

s3cmd --configure
