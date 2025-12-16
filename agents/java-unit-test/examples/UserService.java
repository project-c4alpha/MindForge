package com.example.service;

import com.example.model.User;
import com.example.repository.UserRepository;
import com.example.exception.UserNotFoundException;
import com.example.exception.DuplicateEmailException;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Service for managing user operations.
 * 
 * Example class to demonstrate unit testing best practices.
 */
public class UserService {
    
    private final UserRepository userRepository;
    private final EmailService emailService;
    private final ValidationService validationService;
    
    public UserService(UserRepository userRepository, 
                      EmailService emailService,
                      ValidationService validationService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
        this.validationService = validationService;
    }
    
    /**
     * Creates a new user.
     *
     * @param user the user to create
     * @return the created user with generated ID
     * @throws IllegalArgumentException if user is null or invalid
     * @throws DuplicateEmailException if email already exists
     */
    public User createUser(User user) {
        if (user == null) {
            throw new IllegalArgumentException("User cannot be null");
        }
        
        validationService.validateUser(user);
        
        if (userRepository.existsByEmail(user.getEmail())) {
            throw new DuplicateEmailException("Email already exists: " + user.getEmail());
        }
        
        User savedUser = userRepository.save(user);
        emailService.sendWelcomeEmail(savedUser.getEmail());
        
        return savedUser;
    }
    
    /**
     * Retrieves a user by ID.
     *
     * @param userId the user ID
     * @return the user if found
     * @throws UserNotFoundException if user not found
     * @throws IllegalArgumentException if userId is null
     */
    public User getUserById(Long userId) {
        if (userId == null) {
            throw new IllegalArgumentException("User ID cannot be null");
        }
        
        return userRepository.findById(userId)
            .orElseThrow(() -> new UserNotFoundException("User not found: " + userId));
    }
    
    /**
     * Finds a user by email.
     *
     * @param email the email address
     * @return Optional containing the user if found
     */
    public Optional<User> findByEmail(String email) {
        if (email == null || email.trim().isEmpty()) {
            return Optional.empty();
        }
        
        return userRepository.findByEmail(email);
    }
    
    /**
     * Gets all active users.
     *
     * @return list of active users
     */
    public List<User> getAllActiveUsers() {
        return userRepository.findAll().stream()
            .filter(User::isActive)
            .collect(Collectors.toList());
    }
    
    /**
     * Updates an existing user.
     *
     * @param userId the user ID
     * @param updatedUser the updated user data
     * @return the updated user
     * @throws UserNotFoundException if user not found
     */
    public User updateUser(Long userId, User updatedUser) {
        User existingUser = getUserById(userId);
        
        existingUser.setName(updatedUser.getName());
        existingUser.setEmail(updatedUser.getEmail());
        
        return userRepository.save(existingUser);
    }
    
    /**
     * Deletes a user by ID.
     *
     * @param userId the user ID
     * @throws UserNotFoundException if user not found
     */
    public void deleteUser(Long userId) {
        User user = getUserById(userId);
        userRepository.delete(user);
        emailService.sendGoodbyeEmail(user.getEmail());
    }
    
    /**
     * Counts total number of users.
     *
     * @return the count
     */
    public long countUsers() {
        return userRepository.count();
    }
}
