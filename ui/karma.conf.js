/**
* Copyright (c) 2016 Mirantis Inc.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
* implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

// #docregion
module.exports = function(config) {

  var appBase    = './';         // transpiled app JS and map files
  var appSrcBase = 'app/';       // app source TS files
  var appAssets  = 'base/app/';  // component assets fetched by Angular's compiler

  var testBase    = 'testing/';       // transpiled test JS and map files
  var testSrcBase = 'testing/';       // test source TS files

  config.set({
    basePath: '',
    frameworks: ['jasmine'],
    plugins: [
      require('karma-jasmine'),
      require('karma-firefox-launcher'),
      require('karma-jasmine-html-reporter'),
      require('karma-junit-reporter'),
      require('karma-coverage')
    ],

    customLaunchers: {
      // From the CLI. Not used here but interesting
      // chrome setup for travis CI using chromium
      Chrome_travis_ci: {
        base: 'Chrome',
        flags: ['--no-sandbox']
      }
    },
    files: [
      // System.js for module loading
      'node_modules/systemjs/dist/system.src.js',

      // Polyfills
      'node_modules/core-js/client/shim.js',
      'node_modules/reflect-metadata/Reflect.js',

      // zone.js
      'node_modules/zone.js/dist/zone.js',
      'node_modules/zone.js/dist/long-stack-trace-zone.js',
      'node_modules/zone.js/dist/proxy.js',
      'node_modules/zone.js/dist/sync-test.js',
      'node_modules/zone.js/dist/jasmine-patch.js',
      'node_modules/zone.js/dist/async-test.js',
      'node_modules/zone.js/dist/fake-async-test.js',

      // RxJs
      { pattern: 'node_modules/rxjs/**/*.js', included: false, watched: false },
      { pattern: 'node_modules/rxjs/**/*.js.map', included: false, watched: false },

      // Paths loaded via module imports:
      // Angular itself
      { pattern: 'node_modules/@angular/**/*.js', included: false, watched: false },
      { pattern: 'node_modules/@angular/**/*.js.map', included: false, watched: false },

      { pattern: 'systemjs.config.js', included: false, watched: false },
      { pattern: 'systemjs.config.extras.js', included: false, watched: false },
      'karma-test-shim.js',

      // transpiled application & spec code paths loaded via module imports
      { pattern: appBase + '**/*.js', included: false, watched: true },
      // { pattern: testBase + '**/*.js', included: false, watched: true },


      // Asset (HTML & CSS) paths loaded via Angular's component compiler
      // (these paths need to be rewritten, see proxies section)
      { pattern: appBase + '**/*.html', included: true, watched: true },
      { pattern: appBase + '**/*.css', included: false, watched: true },

      // Paths for debugging with source maps in dev tools
      { pattern: appSrcBase + '**/*.ts', included: false, watched: false },
      { pattern: appBase + '**/*.js.map', included: false, watched: false },
      // { pattern: testSrcBase + '**/*.ts', included: false, watched: false },
      // { pattern: testBase + '**/*.js.map', included: false, watched: false }
    ],

    // Proxied base paths for loading assets
    proxies: {
      // required for component assets fetched by Angular's compiler
      "/app/": appAssets,
      "/app/templates": "/base/app/templates"
    },

    exclude: [],
    reporters: ['progress', 'kjhtml', 'junit', 'coverage'],
    preprocessors: {
      'app/**/*.js': ['coverage']
      // '**/*.html': []
    },

    // karma coverage reporter configuration
    coverageReporter: {
      type: 'text',
      dir: '.',
      subdir: '.',
      file: 'test-coverage.txt'
    },

    junitReporter: {
      outputDir: '',
      outputFile: "test-results.xml",
      suite: '',
      useBrowserName: false,
      nameFormatter: undefined,
      classNameFormatter: undefined,
      properties: {}
    },

    // HtmlReporter configuration
    htmlReporter: {
      // Open this file to see results in browser
      outputFile: '_test-output/tests.html',

      // Optional
      pageTitle: 'Unit Tests',
      subPageTitle: __dirname
    },

    port: 9876,
    colors: true,
    logLevel: config.LOG_INFO,
    autoWatch: true,
    browsers: ['Firefox'],
    singleRun: false
  })
}
