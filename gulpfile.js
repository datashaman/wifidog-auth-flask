var gulp = require('gulp'),
    plugins = require('gulp-load-plugins')();

gulp.task('styles', function() {
    return plugins.merge(
        gulp.src('app/styles/site.scss')
          .pipe(plugins.sass.sync())
          .pipe(plugins.rename('site.css'))
          .pipe(gulp.dest('./tmp')),
        gulp.src([
            'bower_components/purecss/build/pure.css',
            'bower_components/open-iconic/font/css/open-iconic.css',
            'tmp/site.css'
        ]).pipe(plugins.concat('screen.css'))
          .pipe(gulp.dest('./app/static/styles'))
          .pipe(plugins.rename('screen.min.css'))
          .pipe(plugins.uglifycss())
          .pipe(gulp.dest('./app/static/styles'))
    );
});

gulp.task('scripts', function() {
    return plugins.merge(
        gulp.src([
            'bower_components/es5-shim/es5-shim.js',
            'bower_components/html5shiv/html5shiv.js'
        ]).pipe(plugins.concat('ie.js'))
          .pipe(gulp.dest('./app/static/scripts'))
          .pipe(plugins.rename('ie.min.js'))
          .pipe(plugins.uglify())
          .pipe(gulp.dest('./app/static/scripts')),
        gulp.src([
            'bower_components/zepto/zepto.js',
            'bower_components/riot/riot+compiler.js',
            'bower_components/riotcontrol/riotcontrol.js',
            'node_modules/riotgear-modal/dist/rg-modal.js'
        ]).pipe(plugins.concat('interactive.js'))
          .pipe(gulp.dest('./app/static/scripts'))
          .pipe(plugins.rename('interactive.min.js'))
          .pipe(plugins.uglify())
          .pipe(gulp.dest('./app/static/scripts'))
    );
});

gulp.task('fonts', function() {
    return gulp.src([
        'bower_components/open-iconic/font/fonts/**/*'
    ]).pipe(gulp.dest('./app/static/fonts'));
});

gulp.task('default', [ 'styles', 'scripts', 'fonts' ]);
