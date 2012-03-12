define('app/main', ['backbone', 'underscore', 'jquery', 'text!templates/index.html', 'views/nav'],
  function(BB, _, $, template, NavView) {
  return BB.Router.extend({
    template: _.template(template),

    initialize: function() {
      this.version = "0.0.1";
      this.router = new this.router({indexPage: this});
    },
    render: function() {
      var root = this;
      $('body').html(_.template(template)());
      root.$container = $('#content');
      var navView = new NavView({
        model: {
          index: ["Index", '/'],
          signup: ["Sign Up", '/signup'],
          login: ["Login", '/login']
        },
        router: root.router
      });
      //render navbar
      $("#nav-container").html(navView.render());
    },

    router: BB.Router.extend({
      routes: {
        '': "index",
        '/': "index",
        '/signup': "signup",
        '/login': "login"
      },

      initialize: function(options) {
        this.indexPage = options.indexPage;
      },

      index: function() {
        this.indexPage.render();
      },

      signup: function() {
        var root = this; root._ensureContainer();
        curl(['views/signup'], function(SignupView) {
          var signupView = new SignupView({el: root.indexPage.$container});
          signupView.render();
        });
      },

      login: function() {
        var root = this; root._ensureContainer();
        curl(['views/login'], function(LoginView) {
          console.info('login');
        });
      },

      _ensureContainer: function() {
        if(typeof(this.indexPage.$container) == 'undefined')
          this.index();
      }
    })
  });
});

