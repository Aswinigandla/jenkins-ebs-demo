# Jenkins + AWS EBS Persistent Web Application

A beginner project demonstrating a Flask web app deployed to EC2 by Jenkins. The app stores notes at `/mnt/ebs-data/notes.txt`, which must be a separately attached and mounted EBS data volume.

**EBS is block storage, not an application hosting service.** EC2 runs the app; EBS stores persistent data. This project does not create AWS resources automatically. AWS charges may apply.

## Architecture
GitHub -> Jenkins Pipeline -> SSH/SCP -> EC2 Flask app -> EBS volume mounted at `/mnt/ebs-data`

## 1. Launch EC2
1. In AWS Console, choose a region (example `ap-south-1`, Mumbai).
2. Launch an Amazon Linux 2023 EC2 instance. Create/download a key pair; keep the PEM private.
3. In its security group allow SSH TCP 22 from your own public IP. Allow custom TCP 5000 from your own IP for this demo only.
4. Note the EC2 public IPv4 address and Availability Zone.

## 2. Create and mount a separate EBS volume
1. EC2 -> Elastic Block Store -> Volumes -> Create volume. Choose a small size (2–4 GiB for a lab) and the **same Availability Zone** as the instance.
2. Select the new volume -> Actions -> Attach volume -> select your instance.
3. SSH into EC2 from Windows PowerShell in the folder containing your PEM:
   `ssh -i .\YOUR-KEY.pem ec2-user@YOUR-EC2-PUBLIC-IP`
4. Identify the new disk:
   `lsblk`
5. **Carefully confirm which disk is the new, empty EBS data volume. Never format the root disk.** Device names vary; Nitro instances often show `/dev/nvme1n1`.
6. For the confirmed new empty data disk only, create a filesystem (replace device name as needed):
   `sudo mkfs -t xfs /dev/nvme1n1`
7. Mount it:
   `sudo mkdir -p /mnt/ebs-data`
   `sudo mount /dev/nvme1n1 /mnt/ebs-data`
   `sudo chown ec2-user:ec2-user /mnt/ebs-data`
   `df -hT /mnt/ebs-data`
8. Get its UUID: `sudo blkid /dev/nvme1n1`
9. Edit `/etc/fstab` with `sudo nano /etc/fstab` and add this line using the real UUID:
   `UUID=YOUR-UUID /mnt/ebs-data xfs defaults,nofail 0 2`
10. Test before rebooting:
   `sudo umount /mnt/ebs-data`
   `sudo mount -a`
   `df -hT /mnt/ebs-data`
   Fix any fstab errors before rebooting.

## 3. Prepare EC2
Run on EC2:
```bash
sudo dnf update -y
sudo dnf install -y python3
sudo mkdir -p /opt/ebs-demo /mnt/ebs-data
sudo chown ec2-user:ec2-user /opt/ebs-demo /mnt/ebs-data
df -hT /mnt/ebs-data
```
Ensure the last command shows the EBS filesystem mounted there.

## 4. Upload the project to GitHub
Extract this ZIP, create a GitHub repository (e.g. `jenkins-ebs-demo`), and upload all files to the repository root. Do not upload PEM files, AWS keys, or passwords.

## 5. Configure Jenkins
Requirements: Jenkins, Git, Windows OpenSSH client (`ssh.exe`, `scp.exe`), and the Jenkins Credentials Binding plugin.

1. Manage Jenkins -> Credentials -> Global -> Add Credentials.
2. Kind: **SSH Username with private key**; username `ec2-user`; paste/import your PEM private key; ID `ec2-ssh-key`; save.
3. Edit `Jenkinsfile` and replace `REPLACE_WITH_EC2_PUBLIC_IP` with your EC2 public IP/DNS. Commit and push this change.
4. In Jenkins: New Item -> `EBS-Web-App` -> Pipeline.
5. Pipeline definition: **Pipeline script from SCM**; SCM Git; repository URL; branch `*/main` (adjust if needed); Script Path `Jenkinsfile`.
6. Save -> Build Now. Review Console Output.

The Jenkinsfile uses SSH/SCP from a Windows Jenkins agent. If Jenkins runs on Linux, replace the `bat` step with `sh` commands.

## 6. Test
1. Open `http://YOUR-EC2-PUBLIC-IP:5000`.
2. Save a note and refresh the page.
3. On EC2, run `cat /mnt/ebs-data/notes.txt`.
4. Restart the app: `sudo systemctl restart ebs-demo`; the note should remain.

## Troubleshooting
- SSH timeout: verify EC2 is running, public IP is correct, and security-group port 22 allows your IP.
- Permission denied: confirm the key belongs to this EC2 and credential ID is `ec2-ssh-key`.
- Port 5000 unavailable: check security-group rule and `sudo systemctl status ebs-demo`.
- Deploy script says data directory is not a mount point: confirm EBS volume is attached and mounted correctly.
- Public IP changes after stop/start: update `EC2_HOST` in Jenkinsfile.

## Cleanup
Back up anything important. Terminate the EC2 instance and delete the EBS data volume when no longer needed. Deleting a volume permanently deletes its data. Check AWS billing.
