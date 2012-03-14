define('app/main', ['backbone', 'underscore', 'jquery', 'text!templates/index.html', 'views/nav'],
  function(BB, _, $, template, NavView) {
  return BB.View.extend({
    template: _.template(template),

    initialize: function() {
      this.version = "0.0.1";
      this.configRouter();
      this.getCurrentUser();
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
        router: root.router,
        session: root.session
      });
      //render navbar
      $("#nav-container").html(navView.render());
    },

    configRouter: function() {
      var root = this;
      var router = BB.Router.extend({
        routes: {
          '': "layout",
          '/': "layout",
          '/signup': "signup",
          '/login': "login"
        },

        layout: function() {
          root.render();
        },

        signup: function() {
          this._ensureLayout();
          curl(['views/signup'], function(SignupView) {
            var signupView = new SignupView({el: root.$container});
            signupView.render();
          });
        },

        login: function() {
          this._ensureLayout();
          curl(['views/login'], function(LoginView) {
            console.info('login');
          });
        },

        _ensureLayout: function() {
          if(typeof(root.$container) == 'undefined')
            this.layout();
        }

      });

      root.router  = new router();
      BB.history.start();
    },

    getCurrentUser: function() {
      var root = this;
      curl(['models/session'], function(Session) {
        this.session = new Session();
        session.fetch();
      });
    }
  });
});
