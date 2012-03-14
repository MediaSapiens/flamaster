define('views/signup', ['backbone', 'underscore', 'text!templates/signup.html'],
  function(BB, _, template) {
    return BB.View.extend({
      template: _.template(template),

      events: {
        // "submit #signup-form": "submit"
        "click #submit": "submit"
      },

      render: function() {
        return this.$el.html(this.template());
      },

      submit: function(ev) {
        var $form = $(ev.target); //.parents('form');
        console.log(ev.target);
        return false;
      }
  });
});
