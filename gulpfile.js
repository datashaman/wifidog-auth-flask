var es = require('event-stream'),
    gulp = require('gulp'),
    gutil = require('gulp-util'),
    browserSync = require('browser-sync'),
    reload = browserSync.reload,
    plugins = require('gulp-load-plugins')();

function errorHandler(error) {
    console.log(error);
    // gutil.log(gutil.colors.red(error.toString()));
    this.emit('end');
}

function scripts(src, dest) {
    return gulp.src(src)
		.pipe(plugins.concat(dest));
}

function tags(src, dest) {
    return gulp.src(src)
		.pipe(plugins.riot({
			compact: isProduction
		}))
		.pipe(plugins.concat(dest));
}

function sass(src) {
    return plugins.rubySass(src, {
        bundleExec: true
    }).on('error', plugins.rubySass.logError);
}

function riot(src, dest) {
    var options = { compact: false }; // { type: 'es6' };
    return gulp.src(src).pipe(plugins.riot(options)).pipe(plugins.concat(dest));
}

var isProduction = true,
    vendorStyles = [
        'bower_components/pure/build/pure.css',
        'bower_components/open-iconic/font/css/open-iconic.css'
    ],
    siteStyles = [
        'app/assets/styles/**/*.scss'
    ],
    siteTags = [
        'app/assets/tags/**/*.tag'
    ],
    ieScripts = [
        'bower_components/es5-shim/es5-shim.js',
        'bower_components/html5shiv/html5shiv.js'
    ],
    siteScripts = [
        'bower_components/zepto/dist/zepto.js',
        'bower_components/riot/riot.js',
        'bower_components/riot-control/riotcontrol.js',
        'bower_components/marked/lib/marked.js',

        'app/assets/scripts/**/*.js',
        'app/assets/mixins/**/*.js',
        'tmp/tags/**/*.js'
    ];

if(gutil.env.dev === true) {
    isProduction = false;
}

gulp.task('styles', function() {
    return es.concat(gulp.src(vendorStyles), sass(siteStyles))
                .pipe(plugins.concat('screen.min.css'))
                .pipe(plugins.autoprefixer('last 2 versions', 'safari 5', 'ie 8', 'ie 9', 'opera 12.1', 'ios 6', 'android 4', 'Firefox >= 4'))
                // .pipe(isProduction ? plugins.combineMediaQueries({ log: true }) : gutil.noop())
                .pipe(isProduction ? plugins.cssnano() : gutil.noop())
                .pipe(plugins.size())
                .pipe(gulp.dest('./app/static/styles'))
                .pipe(browserSync.stream());
});

gulp.task('scripts', [ 'tags' ], function() {
    return es.concat(
			scripts(ieScripts, 'ie.min.js'),
			scripts(siteScripts, 'site.min.js'))
	     .pipe(isProduction ? plugins.uglify() : gutil.noop()).on('error', errorHandler)
         .pipe(plugins.size())
         .pipe(gulp.dest('./app/static/scripts'));
});

gulp.task('tags', function() {
	return gulp.src([
		'app/assets/tags/**/*.tag'
	])
		.pipe(plugins.riot({
			compact: isProduction
		}))
		.pipe(gulp.dest('./tmp/tags'));
});

gulp.task('fonts', function() {
    return gulp.src([
        'bower_components/open-iconic/font/fonts/**/*'
    ]).pipe(gulp.dest('./app/static/fonts'));
});

gulp.task('build', [ 'styles', 'scripts', 'fonts' ]);

gulp.task('serve', [ 'build' ], function() {
    browserSync({
      proxy: 'localhost:8080'
    });

    gulp.watch(vendorStyles + siteStyles, [ 'styles' ]);
    gulp.watch(ieScripts + siteScripts, [ 'scripts' ]);
    gulp.watch('app/templates/**/*.html', reload);
});

gulp.task('default', [ 'build' ]);
