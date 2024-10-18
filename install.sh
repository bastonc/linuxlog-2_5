#!/bin/bash
name_app='linlog'
git_path='https://github.com/bastonc/linuxlog-2_5.git'
de=$XDG_CURRENT_DESKTOP
dist=`cat /etc/*release | grep -w NAME`
dist_name_dirty=${dist:5}
dist_name=${dist_name_dirty//\"/}
step_run=0 # default step instalation

clear
echo "******************* Install infrastructure components ***********************"
if [[ "$dist_name" == "Fedora" || "$dist_name" == "Fedora Linux" || "$dist_name" == "Rad-hat" || "$dist_name" == "CentOS Linux" ]]
	then
        	sudo dnf install -y git python3-pip python3-qt5 mariadb-server # if git not installed - install it
        	echo "Activate mariadb server for autostart"
        	sudo systemctl enable mariadb
        	echo "Starting mariadb server"
        	sudo systemctl start mariadb
        	sudo dnf install -y socat
        	# sudo dnf install gcc gobject-introspection-devel cairo-gobject-devel pkg-config python3-devel gtk3
        	((step_run=$step_run + 1))
	fi
if [[ "$dist_name" == "Linux Mint" || "$dist_name" == "Ubuntu" || "$dist_name" == "\"Ubuntu\"" || "$dist_name" == "Xubuntu" || "$dist_name" == "Lubuntu" || "$dist_name" == "Lubuntu" || "$dist_name" == "Debian" ]]
	then
    		sudo apt update
        	sudo apt install -y git python3-pip python3-venv python3-pyqt5 mysql-server # if git not installed - install it
        	echo "Activate mariadb server for autostart"
        	sudo systemctl enable mysql
        	echo "Starting mariadb server"
        	sudo systemctl start mysql
        	sudo apt install -y socat
       		# sudo apt install gcc gobject-introspection-devel cairo-gobject-devel pkg-config python3-devel gtk3
       		((step_run=$step_run + 1))
	fi

if [[ "$step_run" == 1 ]]
	then
		echo "****************************** Create linuxlog user for DB ********************************************"
		sudo mysql  -e "FLUSH PRIVILEGES;"
		sudo mysql  -e "CREATE USER 'linuxlog'@'localhost' IDENTIFIED BY 'Linuxlog12#';"
		sudo mysql  -e "GRANT ALL PRIVILEGES ON *.* TO 'linuxlog'@'localhost' WITH GRANT OPTION;"
		sudo mysql  -e "FLUSH PRIVILEGES;"
		echo "All databases (test for user)"
		mysql -u linuxlog -pLinuxlog12# -Bse "show databases;"
		((step_run=$step_run + 1))
	fi

if [[ "$step_run" == 2 ]]
	then
		echo "****************************** Get Source code Linuxlog ********************************************"
		cd $HOME
		if git clone $git_path $name_app
			then
				#echo "Download source code from git repository"
				cd ./$name_app
				((step_run=$step_run + 1))
			else
				echo -en "ERROR: Directory $name_app is not empty or Git not install.\n"
				exit 1
		fi
	fi

if [[ "$step_run" == 3 ]]
	then
		echo '****************************** Create  and activate virtual env ********************************************'
		python3 -m venv env
		source env/bin/activate
		echo 'OK'
		echo "****************************** Install Python requrements ********************************************"
		python3 -m pip install --upgrade pip
		pip3 install -r ~/${name_app}/requirements.txt
		deactivate
		((step_run=$step_run + 1))
	fi

if [[ "$step_run" == 4   ]]
	then
		echo '****************************** Creating run file ********************************************'
		# Create run file
		cat <<EOF > $HOME/$name_app/linlog
#!/bin/bash
cd $HOME/$name_app/
source env/bin/activate
python3 main.py
EOF

		if [[ `chmod +x $HOME/$name_app/linlog` -ne 0 ]]
			then
				echo -en "\nERROR: Can't setup executable bit\n\n"
				exit 1
			fi
		echo 'OK'
		echo '****************************** Creating .desktop file ********************************************'
		# Create desktop.file
		cat > $HOME/$name_app/linlog.desktop << EOF
[Desktop Entry]
Name=LinLog
Comment=Logger for HAM radiostation
Exec= $HOME/$name_app/linlog
Icon=$HOME/$name_app/icon.svg
Terminal=false
Type=Application
Categories=Amateur radio;
EOF
		destination='/usr/share/applications'
		echo "--> copying linlog.desktop file to $destination"
		sudo cp $HOME/$name_app'/linlog.desktop' $destination
		echo 'OK'
		((step_run=$step_run + 1))
	fi

echo "Steps complited: $step_run"
if [[ "$step_run" == 5   ]]
	then
		echo '****************************** Installation complite ********************************************'
		echo 'UR4LGA GL es 73'
	else
		echo "Problem after: $step_run step"
	fi
#echo $dist_name
