/* eslint-disable jsx-a11y/label-has-for */
import React, { PureComponent } from 'react'
import CheckIcon from 'mdi-react/CheckIcon'
import CloseIcon from 'mdi-react/CloseIcon'
import classNames from 'classnames'

class RadioButtonField extends PureComponent {
  static defaultProps = {
    label: '',
    defaultChecked: false,
    radioValue: '',
    disabled: false,
    className: ''
  }

  componentDidMount () {
    if (this.props.defaultChecked) {
      this.props.onChange(this.props.radioValue)
    }
  }

  onChange = () => {
    this.props.onChange(this.props.radioValue)
  }

  render () {
    const {
      disabled, className, name, label, radioValue, value
    } = this.props
    const RadioButtonClass = classNames({
      'radio-btn': true,
      disabled
    })

    return (
      <label
        className={`${RadioButtonClass}${className ? ` radio-btn--${className}` : ''}`}
      >
        <input
          className="radio-btn__radio"
          name={name}
          type="radio"
          onChange={this.onChange}
          checked={value === radioValue}
          disabled={disabled}
        />
        <span className="radio-btn__radio-custom" />
        {className === 'button' ? (
          <span className="radio-btn__label-svg">
            <CheckIcon className="radio-btn__label-check" />
            <CloseIcon className="radio-btn__label-uncheck" />
          </span>) : ''}
        <span className="radio-btn__label">{label}</span>
      </label>
    )
  }
}

const renderRadioButtonField = props => (
  <RadioButtonField
    {...props.input}
    label={props.label}
    defaultChecked={props.defaultChecked}
    disabled={props.disabled}
    radioValue={props.radioValue}
    className={props.className}
  />
)

renderRadioButtonField.defaultProps = {
  label: '',
  defaultChecked: false,
  disabled: false,
  radioValue: '',
  className: ''
}

export default renderRadioButtonField
