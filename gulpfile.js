var es = require('event-stream'),
    gulp = require('gulp'),
    gutil = require('gulp-util'),
    browserSync = require('browser-sync'),
    reload = browserSync.reload,
    plugins = require('gulp-load-plugins')();

function errorHandler(error) {
    // console.log(error);
    gutil.log(gutil.colors.red(error.toString()));
    this.emit('end');
}

function scripts(src, dest) {
    return gulp.src(src)
        .pipe(plugins.concat(dest));
}

function sass(src) {
    return gulp.src(src)
        .pipe(plugins.sass().on('error', plugins.sass.logError));
}

var isProduction = true,
    vendorStyles = [
        'node_modules/purecss/build/pure.css',
        'node_modules/open-iconic/font/css/open-iconic.css'
    ],
    siteStyles = [
        'auth/assets/styles/**/*.scss'
    ],
    ieScripts = [
        'node_modules/es5-shim/es5-shim.js',
        'node_modules/html5shiv/html5shiv.js'
    ],
    siteScripts = [
        'node_modules/marked/lib/marked.js',
        'node_modules/microlib-tabs/dist/tabs-standalone.microlib-latest.js',
        'node_modules/sortablejs/Sortable.js',
        'node_modules/zepto/src/zepto.js',
        'node_modules/zepto/src/ajax.js',
        'node_modules/zepto/src/callbacks.js',
        'node_modules/zepto/src/deferred.js',
        'node_modules/zepto/src/event.js',
        'auth/assets/scripts/**/*.js',
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
        .pipe(gulp.dest('./auth/static/styles'))
        .pipe(browserSync.stream());
});

gulp.task('scripts', function() {
    return es.concat(
        scripts(ieScripts, 'ie.min.js'),
        scripts(siteScripts, 'site.min.js'))
        .pipe(isProduction ? plugins.uglify() : gutil.noop()).on('error', errorHandler)
        .pipe(plugins.size())
        .pipe(gulp.dest('./auth/static/scripts'));
});

gulp.task('fonts', function() {
    return gulp.src([
        'node_modules/open-iconic/font/fonts/**/*'
    ]).pipe(gulp.dest('./auth/static/fonts'));
});

gulp.task('build', [ 'styles', 'scripts', 'fonts' ]);

gulp.task('serve', [ 'build' ], function() {
    browserSync({
        proxy: 'localhost:5000'
    });

    gulp.watch(vendorStyles.concat(siteStyles), [ 'styles' ]);
    gulp.watch(ieScripts.concat(siteScripts), [ 'scripts' ]);
    gulp.watch('auth/blueprints/**/*.html', reload);
    gulp.watch('auth/templates/**/*.html', reload);
});

gulp.task('default', [ 'build' ]);
