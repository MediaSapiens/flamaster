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
  "views/generic_view": function(exports, require, module) {
    (function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  exports.GenericView = (function(_super) {

    __extends(GenericView, _super);

    function GenericView() {
      GenericView.__super__.constructor.apply(this, arguments);
    }

    GenericView.prototype.renderError = function(field, message) {
      var $el, error;
      $el = this.$el.find("form input[name='" + field + "']");
      $el.parents(".control-group").addClass('error');
      error = $(document.createElement('span')).addClass('help-inline error').text(message);
      return $el.after(error);
    };

    GenericView.prototype.clearErrors = function() {
      this.$el.find(".control-group").removeClass('error');
      return this.$el.find("span.help-inline.error").remove();
    };

    return GenericView;

  })(Backbone.View);

}).call(this);

  }
}));
(this.require.define({
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
      return this.safe("<form class='form-horizontal' id='" + id + "'>" + body + "</form>");
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
  "models/profile_model": function(exports, require, module) {
    (function() {
  var __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  exports.ProfileModel = (function(_super) {

    __extends(ProfileModel, _super);

    function ProfileModel() {
      ProfileModel.__super__.constructor.apply(this, arguments);
    }

    ProfileModel.prototype.urlRoot = '/account/profiles/';

    ProfileModel.prototype.initialize = function() {
      this.front = {
        edit: "/#!/profile/" + this.id + "/edit"
      };
      return true;
    };

    ProfileModel.prototype.getUsername = function() {
      var username;
      console.log(this.first_name, this.last_name);
      if ((this.first_name != null) || (this.last_name != null)) {
        username = $.trim("" + this.first_name + " " + this.last_name);
      }
      if (!(username != null) || username.length === 0) {
        username = "please, fill your profile data";
      }
      return username;
    };

    return ProfileModel;

  })(Backbone.Model);

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

    SessionModel.prototype.initial = {
      is_anonymous: true
    };

    return SessionModel;

  })(Backbone.Model);

  exports.LoginModel = (function(_super) {

    __extends(LoginModel, _super);

    function LoginModel() {
      LoginModel.__super__.constructor.apply(this, arguments);
    }

    LoginModel.prototype.defaults = {
      email: '',
      password: ''
    };

    LoginModel.prototype.validate = function(attrs) {
      var response;
      response = {
        status: 'success'
      };
      console.log(attrs.email, this.emailRegex.test(attrs.email));
      if (!this.emailRegex.test(attrs.email)) {
        response.status = 'failed';
        response.email = 'This is not valid email address';
        console.log('email failed');
      }
      if (attrs.password.length === 0) {
        response.status = 'failed';
        response.password = 'You forgot to specify password';
      }
      if (response.status === 'failed') return response;
    };

    return LoginModel;

  })(exports.SessionModel);

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
      '!/': "layout",
      '!/signup': "signup",
      '!/login': "login"
    };

    MainRouter.prototype.initialize = function() {
      return true;
    };

    MainRouter.prototype.layout = function() {
      return app.render();
    };

    MainRouter.prototype.signup = function() {
      return app.render(SignupView);
    };

    MainRouter.prototype.login = function() {
      return app.render(LoginView);
    };

    return MainRouter;

  })(Backbone.Router);

}).call(this);

  }
}));
(this.require.define({
  "routers/profile_router": function(exports, require, module) {
    (function() {
  var ProfileView,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; },
    __slice = Array.prototype.slice;

  ProfileView = require('views/profile_view').ProfileView;

  exports.ProfileRouter = (function(_super) {

    __extends(ProfileRouter, _super);

    function ProfileRouter() {
      ProfileRouter.__super__.constructor.apply(this, arguments);
    }

    ProfileRouter.prototype.routes = {
      '!/profiles/': "index",
      '!/profiles/:id': "show",
      '!/profiles/:id/edit': "edit"
    };

    ProfileRouter.prototype.initialize = function() {
      if (this.view == null) {
        return this.view = new ProfileView({
          routes: this.routes
        });
      }
    };

    ProfileRouter.prototype.index = function() {
      this.bindInject(this.view, 'index');
      return this.view.push({
        action: 'index'
      });
    };

    ProfileRouter.prototype.show = function(id) {
      this.bindInject(this.view, 'show');
      return this.view.push({
        id: id,
        action: 'show'
      });
    };

    ProfileRouter.prototype.edit = function(id) {
      this.bindInject(this.view, 'edit');
      return app.inject(this.view.push({
        id: id,
        action: 'edit'
      }));
    };

    ProfileRouter.prototype.bindInject = function(view, action) {
      var _this = this;
      return view.on(action, function() {
        var args;
        args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
        return app.inject(view.render());
      });
    };

    return ProfileRouter;

  })(Backbone.Router);

}).call(this);

  }
}));
(this.require.define({
  "initialize": function(exports, require, module) {
    (function() {
  var BrunchApplication, HomeView, MainRouter, ProfileRouter,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  BrunchApplication = require('helpers').BrunchApplication;

  MainRouter = require('routers/main_router').MainRouter;

  ProfileRouter = require('routers/profile_router').ProfileRouter;

  HomeView = require('views/home_view').HomeView;

  exports.Application = (function(_super) {

    __extends(Application, _super);

    function Application() {
      Application.__super__.constructor.apply(this, arguments);
    }

    Application.prototype.initialize = function() {
      this.router = new MainRouter;
      return this.profileRouter = new ProfileRouter;
    };

    Application.prototype.render = function(ViewClass, options) {
      var classView;
      if (options == null) options = void 0;
      this.layout();
      if (typeof ViewClass === 'function') {
        classView = (options != null) && new ViewClass(options) || new ViewClass;
        this.inject(classView.render());
        return classView;
      }
    };

    Application.prototype.inject = function(html) {
      this.layout();
      console.log(this.$container);
      return this.$container.html(html);
    };

    Application.prototype.layout = function() {
      if (typeof this.homeView === 'undefined') {
        this.homeView = new HomeView;
        $('body').html(this.homeView.render());
        console.log(this);
        return this.$container = $('#content');
      }
    };

    return Application;

  })(BrunchApplication);

  window.app = new exports.Application;

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
      this.navView = new NavView({
        model: {
          index: ["Index", '!/'],
          signup: ["Sign Up", '!/signup'],
          login: ["Login", '!/login']
        },
        session: this.getCurrentUser()
      });
      return this.getCurrentUser({
        success: function(model, resp) {
          var uid;
          if (!model.get('is_anonymous')) {
            uid = model.get('uid');
            console.log(uid);
            return app.router.navigate("!/profiles/" + uid);
          }
        }
      });
    };

    HomeView.prototype.render = function() {
      this.$el.html(this.template);
      this.$el.find("#nav-container").html(this.navView.render());
      return this.el;
    };

    HomeView.prototype.getCurrentUser = function(options) {
      this.session = new SessionModel;
      if (options != null) {
        return this.session.fetch({
          success: options.success,
          error: options.error
        });
      }
    };

    return HomeView;

  })(Backbone.View);

}).call(this);

  }
}));
(this.require.define({
  "views/login_view": function(exports, require, module) {
    (function() {
  var GenericView, LoginModel, baseContext, serializeForm, _ref,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  LoginModel = require('models/session_model').LoginModel;

  GenericView = require('views/generic_view').GenericView;

  _ref = require('helpers'), baseContext = _ref.baseContext, serializeForm = _ref.serializeForm;

  exports.LoginView = (function(_super) {

    __extends(LoginView, _super);

    function LoginView() {
      LoginView.__super__.constructor.apply(this, arguments);
    }

    LoginView.prototype.className = 'login';

    LoginView.prototype.template = require('./templates/login');

    LoginView.prototype.events = {
      "click #signin-form [type='submit']": "submit"
    };

    LoginView.prototype.initialize = function() {
      var _this = this;
      this.model = new LoginModel;
      return app.homeView.getCurrentUser({
        success: function(model, resp) {
          return _this.model.set(model.toJSON(), {
            silent: true
          });
        }
      });
    };

    LoginView.prototype.render = function() {
      this.$el.html(this.template(baseContext));
      return this.el;
    };

    LoginView.prototype.submit = function(ev) {
      var data,
        _this = this;
      this.clearErrors();
      data = serializeForm($(ev.target).parents('form'));
      this.model.save(data, {
        success: function(model, response) {
          if (!response.is_anonymous) {
            return app.router.navigate("!/profiles/" + response.uid, {
              trigger: true
            });
          }
        },
        error: function(model, response) {
          var field, message, _ref2;
          if (response.responseText != null) {
            _ref2 = JSON.parse(response.responseText);
            for (field in _ref2) {
              message = _ref2[field];
              _this.renderError(field, message);
            }
          } else {
            for (field in response) {
              message = response[field];
              _this.renderError(field, message);
            }
          }
          return console.log(response);
        }
      });
      return false;
    };

    return LoginView;

  })(GenericView);

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
      var _this = this;
      app.router.on("route:layout", function() {
        _this.$el.find("li").removeClass('active');
        return _this.$el.find(".n-index").addClass('active');
      });
      app.router.on("route:login", function() {
        _this.$el.find("li").removeClass('active');
        return _this.$el.find(".n-login").addClass('active');
      });
      return app.router.on("route:signup", function() {
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
  "views/profile_view": function(exports, require, module) {
    (function() {
  var GenericView, ProfileModel, baseContext, serializeForm, _ref,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  ProfileModel = require('models/profile_model').ProfileModel;

  GenericView = require('views/generic_view').GenericView;

  _ref = require('helpers'), baseContext = _ref.baseContext, serializeForm = _ref.serializeForm;

  exports.ProfileView = (function(_super) {

    __extends(ProfileView, _super);

    function ProfileView() {
      ProfileView.__super__.constructor.apply(this, arguments);
    }

    ProfileView.prototype.className = 'profile';

    ProfileView.prototype.template = require('./templates/profile');

    ProfileView.prototype.events = {
      "click a#edit-profile": "edit"
    };

    ProfileView.prototype.actions = function() {
      var _this = this;
      return {
        show: function() {}
      };
    };

    ProfileView.prototype.edit = function(ev) {
      return false;
    };

    ProfileView.prototype.initialize = function(options) {
      return console.log('routes', options.routes);
    };

    ProfileView.prototype.render = function() {
      baseContext = _.extend(baseContext, {
        profile: this.model
      });
      this.$el.html(this.template(baseContext));
      return this.el;
    };

    ProfileView.prototype.push = function(options) {
      var _this = this;
      console.log({
        'pushed': options
      });
      if (typeof options.id !== 'undefined') {
        this.model = new ProfileModel({
          id: options.id
        });
        return this.model.fetch({
          success: function() {
            return _this.trigger(options.action);
          }
        });
      }
    };

    return ProfileView;

  })(GenericView);

}).call(this);

  }
}));
(this.require.define({
  "views/signup_view": function(exports, require, module) {
    (function() {
  var GenericView, SessionModel, baseContext, serializeForm, _ref,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  SessionModel = require('models/session_model').SessionModel;

  GenericView = require('views/generic_view').GenericView;

  _ref = require('helpers'), baseContext = _ref.baseContext, serializeForm = _ref.serializeForm;

  exports.SignupView = (function(_super) {

    __extends(SignupView, _super);

    function SignupView() {
      SignupView.__super__.constructor.apply(this, arguments);
    }

    SignupView.prototype.className = 'signup';

    SignupView.prototype.template = require('./templates/signup');

    SignupView.prototype.events = {
      "click #signup-form button[type='submit']": "submit"
    };

    SignupView.prototype.initialize = function() {
      return this.model = new SessionModel;
    };

    SignupView.prototype.render = function() {
      this.$el.html(this.template(baseContext));
      return this.el;
    };

    SignupView.prototype.submit = function(ev) {
      var $form, formData,
        _this = this;
      $form = $(ev.target).parents('form');
      this.clearErrors();
      formData = serializeForm($form);
      this.model.save(formData, {
        success: function(model, response) {
          if (!response.is_anonymous) {
            return app.router.navigate("!/profile/" + response.uid, {
              trigger: true
            });
          }
        },
        error: function(model, response) {
          var field, message, _ref2, _results, _results2;
          if (response.responseText != null) {
            _ref2 = JSON.parse(response.responseText);
            _results = [];
            for (field in _ref2) {
              message = _ref2[field];
              _results.push(_this.renderError(field, message));
            }
            return _results;
          } else {
            _results2 = [];
            for (field in response) {
              message = response[field];
              _results2.push(_this.renderError(field, message));
            }
            return _results2;
          }
        }
      });
      return false;
    };

    return SignupView;

  })(GenericView);

}).call(this);

  }
}));
