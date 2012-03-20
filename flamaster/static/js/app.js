(function(/*! Brunch !*/) {
  if (!this.require) {
    var modules = {}, cache = {}, require = function(name, root) {
      var module = cache[name], path = expand(root, name), fn;
      if (module) {
        return module;
      } else if (fn = modules[path] || modules[path = expand(path, './index')]) {
        module = {id: name, exports: {}};
        try {
          cache[name] = module.exports;
          fn(module.exports, function(name) {
            return require(name, dirname(path));
          }, module);
          return cache[name] = module.exports;
        } catch (err) {
          delete cache[name];
          throw err;
        }
      } else {
        throw 'module \'' + name + '\' not found';
      }
    }, expand = function(root, name) {
      var results = [], parts, part;
      if (/^\.\.?(\/|$)/.test(name)) {
        parts = [root, name].join('/').split('/');
      } else {
        parts = name.split('/');
      }
      for (var i = 0, length = parts.length; i < length; i++) {
        part = parts[i];
        if (part == '..') {
          results.pop();
        } else if (part != '.' && part != '') {
          results.push(part);
        }
      }
      return results.join('/');
    }, dirname = function(path) {
      return path.split('/').slice(0, -1).join('/');
    };
    this.require = function(name) {
      return require(name, '');
    };
    this.require.brunch = true;
    this.require.define = function(bundle) {
      for (var key in bundle)
        modules[key] = bundle[key];
    };
  }
}).call(this);(this.require.define({
  "helpers": function(exports, require, module) {
    (function() {

  exports.BrunchApplication = (function() {

    function BrunchApplication() {
      var _this = this;
      $(function() {
        _this.initialize(_this);
        return Backbone.history.start();
      });
    }

    BrunchApplication.prototype.initialize = function() {
      return null;
    };

    return BrunchApplication;

  })();

  exports.baseContext = {
    baseField: function(attr, type, placeholder) {
      return this.safe("<input type='" + type + "' name='" + attr + "' id='id_" + attr + "' class='input-large' placeholder='" + placeholder + "' />");
    },
    formFor: function(id, yield) {
      var body, form,
        _this = this;
      form = {
        textField: function(attr, placeholder) {
          return _this.baseField(attr, 'text', placeholder);
        },
        passwdField: function(attr, placeholder) {
          return _this.baseField(attr, 'password', placeholder);
        },
        labelFor: function(attr, name) {
          return _this.safe("<label class='control-label' for='id_" + attr + "'>" + name + "</label>");
        }
      };
      body = yield(form);
      return this.safe("<form class='form-horizontal' id='" + id + "' method='post'>" + body + "</form>");
    }
  };

  exports.serializeForm = function(form) {
    var array, attr, response, _i, _len, _ref;
    _ref = [form.serializeArray(), {}], array = _ref[0], response = _ref[1];
    for (_i = 0, _len = array.length; _i < _len; _i++) {
      attr = array[_i];
      response[attr.name] = attr.value;
    }
    return response;
  };

}).call(this);

  }
}));
(this.require.define({
  "initialize": function(exports, require, module) {
    (function() {
  var BrunchApplication, HomeView, MainRouter,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  BrunchApplication = require('helpers').BrunchApplication;

  MainRouter = require('routers/main_router').MainRouter;

  HomeView = require('views/home_view').HomeView;

  exports.Application = (function(_super) {

    __extends(Application, _super);

    function Application() {
      Application.__super__.constructor.apply(this, arguments);
    }

    Application.prototype.initialize = function() {
      this.router = new MainRouter;
      return this.homeView = new HomeView;
    };

    return Application;

  })(BrunchApplication);

  window.app = new exports.Application;

}).call(this);

  }
}));
(this.require.define({
  "models/session_model": function(exports, require, module) {
    (function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  exports.SessionModel = (function(_super) {

    __extends(SessionModel, _super);

    function SessionModel() {
      SessionModel.__super__.constructor.apply(this, arguments);
    }

    SessionModel.prototype.urlRoot = '/account/sessions/';

    SessionModel.prototype.emailRegex = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;

    SessionModel.prototype.validate = function(attrs) {
      var response;
      response = {
        status: 'success'
      };
      if (!this.emailRegex.test(attrs.email)) {
        response.status = 'failed';
        response.email = 'This is not valid email address';
      }
      if ((attrs.confirm != null) && (attrs.password !== attrs.confirm)) {
        response.status = 'failed';
        response.confirm = "Confirmation don't match";
      }
      if (response.status === 'failed') return response;
    };

    SessionModel.prototype.is_anonymous = function() {
      return console.log(this.toJSON());
    };

    return SessionModel;

  })(Backbone.Model);

}).call(this);

  }
}));
(this.require.define({
  "routers/main_router": function(exports, require, module) {
    (function() {
  var LoginView, SignupView,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  SignupView = require('views/signup_view').SignupView;

  LoginView = require('views/login_view').LoginView;

  exports.MainRouter = (function(_super) {

    __extends(MainRouter, _super);

    function MainRouter() {
      MainRouter.__super__.constructor.apply(this, arguments);
    }

    MainRouter.prototype.routes = {
      '': "layout",
      '/': "layout",
      '/signup': "signup",
      '/login': "login"
    };

    MainRouter.prototype.layout = function() {
      $('body').html(app.homeView.render());
      return this.$container = $('#content');
    };

    MainRouter.prototype.signup = function() {
      var signupView;
      return signupView = this._render(SignupView);
    };

    MainRouter.prototype.login = function() {
      var loginView;
      return loginView = this._render(LoginView);
    };

    MainRouter.prototype._ensureLayout = function() {
      if ($("home-view") != null) return this.layout();
    };

    MainRouter.prototype._render = function(ViewClass) {
      var classView;
      this._ensureLayout();
      classView = new ViewClass;
      this.$container.html(classView.render());
      return classView;
    };

    return MainRouter;

  })(Backbone.Router);

}).call(this);

  }
}));
(this.require.define({
  "views/home_view": function(exports, require, module) {
    (function() {
  var NavView, SessionModel,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  SessionModel = require('models/session_model').SessionModel;

  NavView = require('views/nav_view').NavView;

  exports.HomeView = (function(_super) {

    __extends(HomeView, _super);

    function HomeView() {
      HomeView.__super__.constructor.apply(this, arguments);
    }

    HomeView.prototype.id = 'home-view';

    HomeView.prototype.template = require('./templates/home');

    HomeView.prototype.initialize = function() {
      return this.navView = new NavView({
        model: {
          index: ["Index", '/'],
          signup: ["Sign Up", '/signup'],
          login: ["Login", '/login']
        },
        router: app.router,
        session: this.getCurrentUser()
      });
    };

    HomeView.prototype.render = function() {
      this.$el.html(this.template);
      this.$el.find("#nav-container").html(this.navView.render());
      return this.el;
    };

    HomeView.prototype.getCurrentUser = function() {
      this.session = new SessionModel;
      this.session.fetch();
      return this.session;
    };

    return HomeView;

  })(Backbone.View);

}).call(this);

  }
}));
(this.require.define({
  "views/login_view": function(exports, require, module) {
    (function() {
  var SessionModel, baseContext, serializeForm, _ref,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  SessionModel = require('models/session_model').SessionModel;

  _ref = require('helpers'), baseContext = _ref.baseContext, serializeForm = _ref.serializeForm;

  exports.LoginView = (function(_super) {

    __extends(LoginView, _super);

    function LoginView() {
      LoginView.__super__.constructor.apply(this, arguments);
    }

    LoginView.prototype.className = 'login';

    LoginView.prototype.template = require('./templates/login');

    LoginView.prototype.events = {
      "submit #signin-form": "submit"
    };

    LoginView.prototype.render = function() {
      this.$el.html(this.template(baseContext));
      return this.el;
    };

    LoginView.prototype.submit = function(ev) {
      var data;
      data = serializeForm($(ev.target));
      console.log(data);
      return false;
    };

    return LoginView;

  })(Backbone.View);

}).call(this);

  }
}));
(this.require.define({
  "views/nav_view": function(exports, require, module) {
    (function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  exports.NavView = (function(_super) {

    __extends(NavView, _super);

    function NavView() {
      NavView.__super__.constructor.apply(this, arguments);
    }

    NavView.prototype.tagName = 'ul';

    NavView.prototype.className = "nav nav-pills";

    NavView.prototype.template = require('./templates/nav');

    NavView.prototype.initialize = function(options) {
      var router,
        _this = this;
      router = options.router;
      router.on("route:layout", function() {
        _this.$el.find("li").removeClass('active');
        return _this.$el.find(".n-index").addClass('active');
      });
      router.on("route:login", function() {
        _this.$el.find("li").removeClass('active');
        return _this.$el.find(".n-login").addClass('active');
      });
      return router.on("route:signup", function() {
        _this.$el.find("li").removeClass('active');
        return _this.$el.find(".n-signup").addClass('active');
      });
    };

    NavView.prototype.render = function() {
      this.$el.html(this.template({
        routes: this.model
      }));
      return this.el;
    };

    return NavView;

  })(Backbone.View);

}).call(this);

  }
}));
(this.require.define({
  "views/signup_view": function(exports, require, module) {
    (function() {
  var SessionModel,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  SessionModel = require('models/session_model').SessionModel;

  exports.SignupView = (function(_super) {

    __extends(SignupView, _super);

    function SignupView() {
      SignupView.__super__.constructor.apply(this, arguments);
    }

    SignupView.prototype.template = require('./templates/signup');

    SignupView.prototype.className = 'signup';

    SignupView.prototype.events = {
      "click #signup-form button[type='submit']": "submit"
    };

    SignupView.prototype.initialize = function() {
      return this.$el.find("#signup-form").submit(function() {
        console.log(arguments);
        return false;
      });
    };

    SignupView.prototype.serializeForm = function(form) {
      var array, attr, response, _i, _len, _ref;
      _ref = [form.serializeArray(), {}], array = _ref[0], response = _ref[1];
      for (_i = 0, _len = array.length; _i < _len; _i++) {
        attr = array[_i];
        response[attr.name] = attr.value;
      }
      return response;
    };

    SignupView.prototype.render = function() {
      this.$el.html(this.template());
      return this.el;
    };

    SignupView.prototype.submit = function(ev) {
      var $form, formData, session,
        _this = this;
      $form = $(ev.target).parents('form');
      this.clearErrors();
      formData = this.serializeForm($form);
      session = new SessionModel(formData);
      session.on('error', function(session, error) {
        var field, message, _results;
        _results = [];
        for (field in error) {
          message = error[field];
          _results.push(_this.renderError(field, message));
        }
        return _results;
      });
      session.save({
        success: function() {
          return console.log(arguments);
        },
        error: function() {
          return console.log(arguments);
        }
      });
      return false;
    };

    SignupView.prototype.renderError = function(field, message) {
      var $el, error;
      $el = this.$el.find("form input[name='" + field + "']");
      $el.parents(".control-group").addClass('error');
      error = $(document.createElement('span')).addClass('help-inline error').text(message);
      return $el.after(error);
    };

    SignupView.prototype.clearErrors = function() {
      this.$el.find(".control-group").removeClass('error');
      return this.$el.find("span.help-inline.error").remove();
    };

    return SignupView;

  })(Backbone.View);

}).call(this);

  }
}));
