#!/usr/bin/perl

#    cpfm-module-installer.pm - Module Installer Helper for WHM/cPanel.
#    Author: Farhad Malekpour <fm@farhad.ca>
#    Copyright (C) 2011 Dayana Networks Ltd.
#    More information can be found at http://www.cpios.com
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms as perl itself.
#

BEGIN {
	push(@INC,"/usr/local/cpanel");
	push(@INC,"/usr/local/cpanel/whostmgr/docroot/cgi");
}


use lib '/usr/local/cpanel/';
use Whostmgr::ACLS ();
use Whostmgr::HTMLInterface ();
use Whostmgr::Mail::RBL     ();
use Cpanel::Encoder::Tiny   ();
use Cpanel::Form            ();
use Cpanel::HttpRequest		();
use Cpanel::CPAN::MIME::Base64::Perl ();
use Cpanel::CPAN::Digest::Perl::MD5  ();

Whostmgr::ACLS::init_acls();

print "Content-type: text/html\n\n";

my %FORM = Cpanel::Form::parseform();
print "FORM ACTION: [".$FORM{'action'}."]\n";




if ( (!Whostmgr::ACLS::hasroot() || !Whostmgr::ACLS::checkacl( 'all' )) && ($FORM{'action'} ne 'update-hm-wrap') )
{
	print qq{
	<br />
	<br />
	<div align="center"><h1>Permission denied</h1></div>
	};
	exit;
}



if($FORM{'action'} eq 'install-module')
{
	foreach my $key (sort keys  %FORM)
	{
	if($key =~ m/^cgi-/)
	{
		my $fn = $key;
		$fn =~ s/^cgi-//;
			my $fc = Cpanel::CPAN::MIME::Base64::Perl::decode_base64($FORM{$key});

			print "Saving [$fn] => [$fc]\n";

			open(FILE,">/usr/local/cpanel/whostmgr/docroot/cgi/$fn");
			print FILE $fc;
			close(FILE);
			chmod 0700, "/usr/local/cpanel/whostmgr/docroot/cgi/$fn";
		}
	if($key =~ m/^cpanel-/)
	{
		my $fn = $key;
		$fn =~ s/^cpanel-//;
			my $fc = Cpanel::CPAN::MIME::Base64::Perl::decode_base64($FORM{$key});
			open(FILE,">/usr/local/cpanel/Cpanel/$fn");
			print FILE $fc;
			close(FILE);
			chmod 0644, "/usr/local/cpanel/Cpanel/$fn";
		}
	if($key =~ m/^whm-/)
	{
		my $fn = $key;
		$fn =~ s/^whm-//;
			my $fc = Cpanel::CPAN::MIME::Base64::Perl::decode_base64($FORM{$key});
			open(FILE,">/usr/local/cpanel/Whostmgr/$fn");
			print FILE $fc;
			close(FILE);
			chmod 0644, "/usr/local/cpanel/Whostmgr/$fn";
		}
	}
	print qq{
	<br />
	<br />
	<div align="center"><h1>Module installed</h1></div>
	};
	exit;
}

if($FORM{'action'} eq 'update-hm-wrap')
{
	my @tempFiles;
	my $requiredVersion = $FORM{'version'};
	$requiredVersion =~ s/[^0-9.]//g;
	if($requiredVersion eq "")
	{
		print qq{<br /><br /><div align="center"><h1>Version is missing</h1></div>};
		exit;
	}
	if(-f '/var/spool/hmupdates')
	{
		unlink('/var/spool/hmupdates');
	}
	if(! -d "/var/spool/hmupdates")
	{
		mkdir("/var/spool/hmupdates",0700);
	}
	chmod 0700, "/var/spool/hmupdates";

	my $moduleName = 'hm_iphone_wrap_'.$requiredVersion.'.cgi';
	my $moduleNameTemp = 'hm_iphone_wrap_'.$requiredVersion.'-'.rand(10000).'.cgi';
	my $installedFullVersion = '';

	if(open(FILE,"/usr/local/cpanel/whostmgr/docroot/cgi/$moduleName"))
	{
		while(<FILE>)
		{
			my $line = $_;
			$line =~ s/[\r\n\s]//g;
			if($line =~ m/^\#HMIOS\-VERSION:(.*)$/)
			{
				$installedFullVersion = $1;
				last;
			}
		}
		close(FILE);
	}



	my $httpClient = Cpanel::HttpRequest->new( 'hideOutput' => 1 );

	unlink("/var/spool/hmupdates/".$moduleNameTemp);
	unlink("/var/spool/hmupdates/".$moduleNameTemp.'.md5');
	$httpClient->download( 'http://sync.cpios.com/?module=hm_iphone_wrap&mode=file&major='.$requiredVersion, '/var/spool/hmupdates/' . $moduleNameTemp );
	$httpClient->download( 'http://sync.cpios.com/?module=hm_iphone_wrap&mode=md5&major='.$requiredVersion, '/var/spool/hmupdates/' . $moduleNameTemp . '.md5' );

	push(@tempFiles,$moduleNameTemp);
	push(@tempFiles,$moduleNameTemp.'.md5');

	if(! -e "/var/spool/hmupdates/".$moduleNameTemp || ! -e "/var/spool/hmupdates/".$moduleNameTemp.'.md5')
	{
		_cleanupTemp(@tempFiles);
		print qq{<br /><br /><div align="center"><h1>Unable to download the updated version of the module</h1></div>};
		exit;
	}

	$md5o = Cpanel::CPAN::Digest::Perl::MD5->new();
	open(FILE, "/var/spool/hmupdates/".$moduleNameTemp);
	my $buf;
	while ( read( FILE, $buf, 1024 ) ){	$md5o->add($buf);	}
	my $localMD5 = lc($md5o->hexdigest);
	$localMD5 =~ s/[\r\n\s]//g;
	close(FILE);

	open(FILE, "/var/spool/hmupdates/".$moduleNameTemp.'.md5');
	my $remoteMD5 = <FILE>;
	close(FILE);
	$remoteMD5 =~ s/[\r\n\s]//g;
	$remoteMD5 = lc($remoteMD5);

	if($localMD5 ne $remoteMD5)
	{
		_cleanupTemp(@tempFiles);
		print qq{<br /><br /><div align="center"><h1>MD5 does not match [$localMD5][$remoteMD5]</h1></div>};
		exit;
	}


	open(SRC, "/var/spool/hmupdates/".$moduleNameTemp);
	open(DST, ">/usr/local/cpanel/whostmgr/docroot/cgi/".$moduleName);
	my $buf;
	while (<SRC>)
	{
		print DST $_;
	}
	close(SRC);
	close(DST);

	chmod 0700, "/usr/local/cpanel/whostmgr/docroot/cgi/".$moduleName;



	_cleanupTemp(@tempFiles);
	print qq{<br /><br /><div align="center"><h1>Module has updated</h1></div>};
	exit;
}

sub _cleanupTemp
{
	my @list = @_;
	foreach my $file (@list)
	{
		unlink('/var/spool/hmupdates/'.$file);
	}
}


print qq{
<br />
<br />
<div align="center"><h1>Invalid action</h1></div>
};

