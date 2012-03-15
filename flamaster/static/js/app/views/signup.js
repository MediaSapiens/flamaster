define('views/signup', ['backbone', 'underscore', 'models/session', 'text!templates/signup.html'],
  function(BB, _, Session, template) {
    return BB.View.extend({
      template: _.template(template),

      events: {
        // "submit #signup-form": "submit"
        "click #submit": "submit"
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
            user = new Session(formData);
        user.save({
          success: function() {
            console.log(arguments);
          },
          error: function() {
            console.log(arguments);
          }
        });
        return false;
      }
  });
});
