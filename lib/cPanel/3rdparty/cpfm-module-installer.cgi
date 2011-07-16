#!/usr/bin/perl

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
use Cpanel::CPAN::MIME::Base64::Perl ();

Whostmgr::ACLS::init_acls();

print "Content-type: text/html\n\n";
#Whostmgr::HTMLInterface::defheader();

if ( !Whostmgr::ACLS::hasroot() || !Whostmgr::ACLS::checkacl( 'all' ) ) 
{
    print qq{
    <br />
    <br />
    <div align="center"><h1>Permission denied</h1></div>
    };
    exit;
}

my %FORM = Cpanel::Form::parseform();

print "FORM ACTION: [".$FORM{'action'}."]\n";

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

print qq{
<br />
<br />
<div align="center"><h1>Invalid action</h1></div>
};

