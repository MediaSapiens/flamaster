define('views/signup', ['backbone', 'underscore', 'models/session', 'text!templates/signup.html'],
  function(BB, _, Session, template) {
    return BB.View.extend({
      template: _.template(template),

      events: {
        // "submit #signup-form": "submit",
        "click #submit": "submit"
      },

      initialize: function() {
        // this.$el.find("#signup-form").submit(function() {
        //   console.log(arguments);
        //   return false;
        // });
      },

      serializeForm: function(form) {
        var array = form.serializeArray(),
            response = {};
        _.each(array, function(obj, idx) {
          response[obj.name] = obj.value;
        });
        return response;
      },

      render: function() {
        return this.$el.html(this.template());
      },

      submit: function(ev) {
        var $form = $(ev.target).parents('form'),
            formData = this.serializeForm($form),
            session = new Session(formData);
        // error event listener
        session.on('error', function(model, error) {
          _.each(error, function(message, attr) {
            // render error messages
            this.renderError(attr, message);
          }, this);
          return false;
        }, this);

        session.save({
          success: function() {
            console.log(arguments);
          },
          error: function() {
            console.log(arguments);
          }
        });
        console.log(arguments);
        return false;
      },

      renderError: function(field, message) {
        var el = $el.find("form input[name='" + field + "']");
        console.log(el);
        return false;
      }
  });
});
