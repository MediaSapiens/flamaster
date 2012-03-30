class exports.GenericView extends Backbone.View

  renderError: (field, message) ->
    $el = @$el.find "form input[name='#{field}']"
    $el.parents(".control-group").addClass 'error'
    error = $(document.createElement('span')).addClass('help-inline error').text message
    $el.after error

  clearErrors: ->
    @$el.find(".control-group").removeClass 'error'
    @$el.find("span.help-inline.error").remove()