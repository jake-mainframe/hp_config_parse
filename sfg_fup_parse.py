
import argparse 
arg_parser = argparse.ArgumentParser()

arg_parser.add_argument("--fup", type=str)
arg_parser.add_argument("--sfg", type=str)
args = arg_parser.parse_args()

diskfup_list = [] 

sfg_vol_dict = {}
sfg_subvol_dict = {}
sfg_diskfile_dict = {}


class diskfup:
  def __init__(self, volume, subvol, diskfile, disk_type, disk_rwep):
    self.volume = volume
    self.subvol = subvol
    self.diskfile = diskfile
    self.disk_rwep = disk_rwep
    self.disk_type = disk_type


def parse_sfg_line(line):
	if ("\\*.*.*" in line) or ("\\*.*,*" in line):
		world_access = ""
		if "R" in line:
			world_access += "R,"
		if "W" in line:
			world_access += "W,"
		if "E" in line:
			world_access += "E,"
		if "P" in line:
			world_access += "P"
		return world_access
	return ""

def parse_safe():
	world_access = ""
	section = "none"
	with open(args.sfg,"r") as fupfile:
		for line in fupfile:
			line = line.strip()
			if ((section != "none") & (len(line) > 0)):
				if (section == "volume"):
					if(line[0] == "$"):
						world_access = ""
						volume = line
					else:
						world_access += parse_sfg_line(line)		
						sfg_vol_dict[volume] = world_access			
				elif (section == "subvol"):
					if(line[0] == "$"):
						world_access = ""
						subvol = line
					else:
						world_access += parse_sfg_line(line)
						sfg_subvol_dict[subvol] = world_access
				elif (section == "diskfile"):
					if(line[0] == "$"):
						world_access = ""
						vol_subvol = line
						get_diskfile = True
					elif(get_diskfile):
						second_line = line.split()
						diskfile = vol_subvol + "." + second_line[0]
						get_diskfile = False
					else:
						world_access += parse_sfg_line(line)
						sfg_diskfile_dict[diskfile] = world_access
			if (line =="=INFO VOLUME $*,DETAIL"):
				section = "volume"
				world_access = ""
				volume = ""
			if (line =="=INFO SUBVOL $*.*,DETAIL"):
				section = "subvol"
				world_access = ""
				subvol = ""
			if (line =="=INFO DISKFILE $*.*.*,DETAIL"):
				section = "diskfile"
				world_access = ""
				diskfile = ""
				get_diskfile = False



def parse_fup():
	volume = ""
	subvol = ""
	with open(args.fup,"r") as fupfile:
		for line in fupfile:
			line = line.strip()
			if (len(line) != 0):
				if (line[0] == "$"):
					path = line.split(".")
					if (len(path) == 2):
						volume = path[0]
						subvol = path[1]
				elif(len(line.split()) > 3):
					diskfile_info = line.split()
					if  (diskfile_info[1] == "O"):
						disk_type = diskfile_info[2]
					else:
						disk_type = diskfile_info[1]
					for field in diskfile_info:
						if ((len(field) == 4) &  (not any(map(str.isdigit, field))) & (field != "OSS+")):
							diskfup_list.append(diskfup(volume, subvol, diskfile_info[0], disk_type, field))
						

def find_world(char, index):
	for diskfup in diskfup_list:
		
		reason = ""
		diskfup_fullfile = diskfup.volume + "." + diskfup.subvol + "." + diskfup.diskfile
		try:
			sfg_diskfile = sfg_diskfile_dict[diskfup_fullfile]
			if char in sfg_diskfile:
				reason = "SAFEGUARD DISKFILE"
		except KeyError:
			if (diskfup.disk_rwep[index] == "N"):
				diskfup_subvol = diskfup.volume + "." + diskfup.subvol
				try:
					sfg_subvol = sfg_subvol_dict[diskfup_subvol]
					if char in sfg_subvol:
						reason = "SAFEGUARD SUBVOL + GUARDIAN DISKFILE"
				except KeyError:
					try:
						sfg_vol = sfg_vol_dict[diskfup.volume]
						if char in sfg_vol:
							reason = "SAFEGUARD VOL + GUARDIAN DISKFILE"
					except KeyError:
						reason = "NO SAFEGUARD + GUARDIAN DISKFILE"
		if (reason != ""):
			print(reason)
			print(diskfup_fullfile)
			print(diskfup.disk_type)
			print("")


def main(): 


	parse_fup()
	parse_safe()
	print("------------------------")
	print("World Readable Diskfiles")
	print("------------------------")
	find_world("R",0)
	print("------------------------")
	print("----END OF SECTION------")
	print("------------------------")
	print("------------------------")
	print("World Writable Diskfiles")
	print("------------------------")
	find_world("W",1)
	print("------------------------")
	print("----END OF SECTION------")
	print("------------------------")
	print("------------------------")
	print("World Purgable Diskfiles")
	print("------------------------")
	find_world("P",3)	
	print("------------------------")
	print("----END OF SECTION------")
	print("------------------------")





if __name__ == "__main__":
    main()