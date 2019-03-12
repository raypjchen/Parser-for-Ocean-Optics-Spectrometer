import glob, os, shutil, re

def natural_key(string_):
    """See http://www.codinghorror.com/blog/archives/001018.html"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]

def getDatDirPath( par_dir ):
    # find all subfolders in parent directory
    dir_path = sorted( glob.glob( os.path.join( par_dir, '*' )), key=natural_key )
    dir_path = [ d for d in dir_path if os.path.isdir( d )]
    if not dir_path: print( getDatDirPath.__name__+'()', 'No directory was found in', par_dir )
    return dir_path

def getDatPath( par_dir, fpath_reg ):
    dat_path_reg = os.path.join( par_dir, fpath_reg )
    dat_path = sorted( glob.glob( dat_path_reg ), key=natural_key )
    if not dat_path: print( getDatPath.__name__+'()', 'No \"{}\" data file was found in'.format(fpath_reg), par_dir )
    return dat_path

def getFileName( par_dir, fpath_reg ):
    file_path = getDatPath( par_dir, fpath_reg )
    file_name = [ p.split( os.sep )[-1] for p in file_path ]
    if not file_name: print( getFileName.__name__+'()', 'No file was found in', par_dir )
    return file_name

def delete_file( sdir, fname ):
    fpath = glob.glob( os.path.join( sdir, fname ))
    for fp in fpath:
        if os.path.exists( fp ):
            try:
                #print('\tDelete:', fp )
                e = os.remove( fp )
            except OSError:
                print ('\t{0}\tError: {1} - {2}.'.formt( pre_run.__name__, e.filename, e.strerror))

def copy_file( fname, sdir ):
    try:
        #print('\tCopy \'{0}\' to \'{1}\'.'.format( fname, sdir ))
        shutil.copy( fname, sdir )
    except FileNotFoundError:
        print('\tFailed to copy \'{0}\' to \'{1}\' because \'{0}\' or \'{1}\' do not exist.'.format( fname, sdir ))
    except NotADirectoryError:
        print('\tNot a directory: \'{0}\' or \'{1}\' do not exist or '.format( fname, sdir ))

def copy_file_as( src, dst ):
    try:
        #print('\tCopy \'{0}\' as \'{1}\'.'.format( src, dst ))
        shutil.copyfile( src, dst )
    except FileNotFoundError:
        print('\tFailed to copy \'{0}\' as \'{1}\' because \'{0}\' does not exist.'.format( src, dst ))
    except NotADirectoryError:
        print('\tNot a directory: \'{0}\' or \'{1}\' do not exist.'.format( src, dst ))
    
def append_file( patch_path, source_path ):
    try:
        with open( patch_path, 'r' ) as pch:
            patch = pch.readlines()
        try:
            #print('\tAppend {} to {}'.format( patch_path, source_path ))
            with open( source_path, 'a+' ) as src:
                for p in patch:
                    src.write(p)
        except FileNotFoundError:
            print('\tSource file does not exist. Failed to append.')
        except NotADirectoryError:
            print('\tNot a directory: \'{}\' do not exist.'.format( patch_path ))
    except FileNotFoundError:
        print('\tPatch file does not exist. Failed to append.')
    except NotADirectoryError:
        print('\tNot a directory: \'{}\' do not exist.'.format( patch_path ))
