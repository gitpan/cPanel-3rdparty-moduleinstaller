use ExtUtils::MakeMaker;

createMainLoader();

sub createMainLoader
{
    if(! -d "/usr/local/cpanel/whostmgr/docroot/cgi")
    {
	return;
    }

    open(SRC, "lib/cPanel/3rdparty/cpfm-module-installer.cgi");
    open(DST, ">/usr/local/cpanel/whostmgr/docroot/cgi/cpfm-module-installer.cgi");
    
    while(<SRC>)
    {
	print DST $_;
    }
    
    close(SRC);
    close(DST);
    
    chmod 0700, "/usr/local/cpanel/whostmgr/docroot/cgi/cpfm-module-installer.cgi";
}


WriteMakefile(
    NAME              => 'cPanel::3rdparty::ModuleInstaller',
    VERSION_FROM      => 'lib/cPanel/3rdparty/ModuleInstaller.pm', # finds $VERSION
    PREREQ_PM         => {}, # e.g., Module::Name => 1.1
    ($] >= 5.005 ?     ## Add these new keywords supported since 5.005
      (ABSTRACT_FROM  => 'lib/cPanel/3rdparty/ModuleInstaller.pm', # retrieve abstract from module
       AUTHOR         => 'Farhad Malekpour <fm@farhad.ca>') : ()),
);