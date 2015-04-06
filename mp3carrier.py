#!/usr/bin/python
#coding: utf-8

import os.path
import shutil, sys, getopt

class mp3carrier:
    
    supported_file_ext = (".mp3", ".ape")
    @classmethod
    def update_playlist(cls, playlist, mp3path, dst_dir):

        if not os.path.isfile(playlist):
            raise Exception('The filename specified is not a valid path of existing file.')
        
        mp3path = mp3carrier.__trim_filepath(mp3path)
        
        mp3carrier.__validate_filepath_and_dirpath(mp3path, dst_dir)
        
        # generate the name of backup playlist 
        filenamepair = os.path.splitext(playlist)
        pairlist = list(filenamepair)
        newfilename = pairlist[0] + "_bak"  + pairlist[1]
    
        # split the original file path    
        src_file_pair = os.path.split(mp3path)
        src_dir = src_file_pair[0]
        #filename = src_file_pair[1]
        
        if not os.path.isdir(dst_dir):
            raise Exception('The destination location specified is not a valid path of existing directory.')
            
        if dst_dir[-1] == os.path.sep:
            dst_dir = dst_dir[0:-1]

        file = open(playlist, "r+")
        file_w = open(newfilename, "w+")
        try:
            for line in file:
                if line in ('\n', '\t', '\r', ' '):
                    file_w.write(line)
                #elif line.find(mp3path) != -1:        # find() should be rewrote, otherwise, it cannot handle "mp3" and "MP3" correctly
                elif mp3carrier.__find_mp3path_in_string(line, mp3path):
                    line = line.replace(src_dir, dst_dir, 1)   # if the 3rd argument not specified. the part of file name may be replaced as well
                    file_w.write(line)
                else:
                    file_w.write(line)
        except IOError as ex:
            print(str(ex))
        finally:
            file.close()
            file_w.close()

        os.remove(playlist)
        os.rename(newfilename, playlist)

    @classmethod        
    def move_file(cls, src_path, dst_dir):
        src_path = mp3carrier.__trim_filepath(src_path)
        mp3carrier.__validate_filepath_and_dirpath(src_path, dst_dir)
        shutil.move(src_path, dst_dir)
        return True
    
    @classmethod
    def check_playlist_supported(cls, playlist_path):
        playlist_path = mp3carrier.__trim_filepath(playlist_path)
        path_pair = os.path.splitext(playlist_path)
        support_ext = ('.m3u', '.txt')
        if path_pair[1] in support_ext:
            if os.path.isfile(playlist_path):
                return True
        return False
    
    @classmethod
    def __trim_filepath(cls, filepath):
        specific_symbol = (' ', '\n', '\t', '\r')
        '''while filepath[-1] in specific_symbol:
            filepath = filepath[:-1]
        return filepath'''
        
        i = 1
        while filepath[-i] in specific_symbol:
            i += 1
            if(i > len(specific_symbol)):
                break
        
        if i == 1:
            return filepath
        elif i >= (len(filepath) + 1):
            return ''
        else:
            return filepath[:-(i-1)]
    
    @classmethod
    def __validate_filepath_and_dirpath(cls, filepath, dirpath):
        if not os.path.isfile(filepath):
            raise Exception('The src_path specified is not a valid path of existing file.')
        
        if not os.path.isdir(dirpath):
            raise Exception('The dst_dir specified is not a valid path of existing directory.')
        
        return True
    
    @classmethod
    def __find_mp3path_in_string(cls, strline, mp3path):
        strline = mp3carrier.__trim_filepath(strline)
        path_pair = os.path.splitext(mp3path)
        for str_item in mp3carrier.supported_file_ext:
            if path_pair[1].lower() == str_item:
                ext_len = len(str_item)
                break
        else:
            return False
        
        return ((strline[(-ext_len):].lower() ==  path_pair[1].lower()) and (strline[:(-ext_len)].endswith(path_pair[0])))

def version():
    print ("mp3carrier v1.0.0")

def usage():
    version()
    print ("usage: python mp3carrier [option] -p playlist -d directory [-i mp3list|mp3 path]")
    
def main(argv):
    if len(argv) < 2 or len(argv) > 9:
        print("Invalid arguments.")
        usage()
        sys.exit(1)
    
    format_string = ("p:d:hv", "p:d:i:hv")
    
    try:
        if "-i" in argv:
            opts, args = getopt.getopt(sys.argv[1:], format_string[1], ["version", "help"])
        else:
            opts, args = getopt.getopt(sys.argv[1:], format_string[0], ["version", "help"])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    
    playlist = ""
    inputfile = ""
    inputlist = ""
    destdir = ""
    
    for op, value in opts:
        if op == "-p":
            playlist = value
        elif op == "-i":
            inputlist = value
        elif op == "-d":
            destdir = value
        elif op in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif op in ("-v", "--version"):
            version()
            sys.exit(0)
        else:
            print("Unhanded option.")
            usage()
            sys.exit(3)
    
    if(len(args) < 2 and len(args) >0):
        inputfile = args[0]
    elif(len(args) > 2):
        print("Unrecognised arguments.")
        usage()
        sys.exit(3)
        
    if inputfile != '':
        if mp3carrier.check_playlist_supported(playlist):
            mp3carrier.update_playlist(playlist, inputfile, destdir)
            mp3carrier.move_file(inputfile, destdir)
        else:
            raise Exception("Not supported playlist.")
    else:
        if mp3carrier.check_playlist_supported(playlist):
            if os.path.isfile(inputlist):
                listfile = open(inputlist, "r")
                try:
                    for line in listfile:
                        mp3carrier.update_playlist(playlist, line, destdir)
                        mp3carrier.move_file(line, destdir)
                except IOError as ioerr:
                    print(str(ioerr))
                finally:
                    listfile.close()
            else:
                raise Exception("Invalid file list.")
        else:
            raise Exception("Not supported playlist.")
    
    sys.exit(0)
        
if __name__=='__main__':
    main(sys.argv)
