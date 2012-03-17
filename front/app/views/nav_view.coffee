class exports.NavView extends Backbone.View
  tagName: 'ul'
  className: "nav nav-pills"
  template: require('./templates/nav')

  initialize: (options) ->
    router = options.router
    # have to refactor this
    router.on "route:layout", =>
      @$el.find("li").removeClass 'active'
      @$el.find(".n-index").addClass 'active'

    router.on "route:login", =>
      @$el.find("li").removeClass 'active'
      @$el.find(".n-login").addClass 'active'

    router.on "route:signup", =>
      @$el.find("li").removeClass 'active'
      @$el.find(".n-signup").addClass 'active'

  render: ->
    @$el.html @template routes: @model
    @el
