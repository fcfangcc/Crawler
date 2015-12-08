var casper = require('casper').create({
	pageSettings:{
		loadImages: false,
		loadPlugins: false
	},
	verbose: true,
	logLevel: "error"
});

//var fs = require('fs');
//var url = casper.cli.raw.get('url');
var url = 'http://tieba.baidu.com/f?kw=炉石传说&fr=home';
casper.userAgent('Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36');

casper.start(url, function() {
    //this.echo(this.getTitle());
	this.getTitle();
});

casper.then(function(){
	this.page.switchToChildFrame(0);
	//fs.write("E:\\eclipse4.4.1\\python\\study\\Crawler\\test\\1.html", this.getHTML(), 'w');
	this.echo(this.getHTML());
});

casper.run();
