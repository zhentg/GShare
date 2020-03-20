Debug
##    3/20/2020
###        Case 1
            Reported by
                Hengyi Cao
                    Jidong's student
            Hardware
                Nvidia Quadro M620
            Bug
                打开PyMOL后，会不停提示gl错误
                    WARNING: glDrawBuffer caused GL error
            Solution
                在Nvidia控制面板中，把这个立体打开
                    o
###        Case 2
            Reported by
                Xingnian Fu
            Bug
                OpenBabel can not be load, even the path is correctly set
            Deduction
                in CMD window, execute obabel.exe to check if obabel can run
                    error window pops up reporting missing files
                        msvs120.dll
                        msvsp120.dll
            Solution
                Download Visual C++ Redistributable Packages for Visual Studio 2013 64bit version and install it
                    <https://www.microsoft.com/en-us/download/confirmation.aspx?id=40784>
##    2/27/2020
###        Case 1
            pymol进行vina对接是一次只能对接一个配体吗？我选了all就会出错
                solution
                    D:\cadd\pymolAllInOne\Pymol-script-repo\plugins\autodock_plugin_windows.py
                        Line 2415
                            old
                                pth = self.ligand_dic['VS_DIR']
                                    self.ligand_dic['VS_DIR']
                                        this variable is only defined if user click "Import" at the "Ligand" panel
                            new
                                            try:
                pth = self.ligand_dic['VS_DIR']
            except:
                pth = self.work_path_location
                                    self.ligand_dic['VS_DIR']
                                        solution is if this variable is not defined, then use current working directory to dock all the ligands
###        Case 2
            docking log file can not be overwrite
                deduction
                    log file are written by Thread_log
                        Thread_log(outfile_log, self.docking_page_log_text, self)
                        Thread_log
                            is defined  class in the script
                            Line 266
                                old
                                    if 'ADPLUGIN_NO_OUTPUT_REDIRECT' not in os.environ:
                                new
                                    if 'ADPLUGIN_NO_OUTPUT_REDIRECT' in os.environ:
                                        this will avoid calling Tail class
