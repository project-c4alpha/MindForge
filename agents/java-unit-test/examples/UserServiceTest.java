package com.example.service;

import com.example.model.User;
import com.example.repository.UserRepository;
import com.example.exception.UserNotFoundException;
import com.example.exception.DuplicateEmailException;

import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnitRunner;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;
import static org.mockito.ArgumentMatchers.*;

/**
 * Unit tests for {@link UserService}.
 * 
 * <p>Test coverage includes:
 * <ul>
 *   <li>User creation (validation, duplication, email notification)</li>
 *   <li>User retrieval (by ID, by email, all active users)</li>
 *   <li>User updates</li>
 *   <li>User deletion</li>
 *   <li>Edge cases (null inputs, empty results, boundary conditions)</li>
 *   <li>Exception scenarios</li>
 * </ul>
 */
@RunWith(MockitoJUnitRunner.class)
public class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    @Mock
    private EmailService emailService;
    
    @Mock
    private ValidationService validationService;
    
    @InjectMocks
    private UserService userService;
    
    private User testUser;
    private User activeUser;
    private User inactiveUser;
    
    @Before
    public void setUp() {
        testUser = new User(1L, "test@example.com", "Test User", true);
        activeUser = new User(2L, "active@example.com", "Active User", true);
        inactiveUser = new User(3L, "inactive@example.com", "Inactive User", false);
    }
    
    // ========================================
    // User Creation Tests
    // ========================================
    
    @Test
    public void givenValidUser_whenCreateUser_thenUserIsSavedAndReturned() {
        // Given
        when(userRepository.existsByEmail(testUser.getEmail())).thenReturn(false);
        when(userRepository.save(testUser)).thenReturn(testUser);
        doNothing().when(validationService).validateUser(testUser);
        
        // When
        User result = userService.createUser(testUser);
        
        // Then
        assertThat(result).isNotNull();
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getEmail()).isEqualTo("test@example.com");
        assertThat(result.getName()).isEqualTo("Test User");
        verify(userRepository).save(testUser);
    }
    
    @Test
    public void givenValidUser_whenCreateUser_thenWelcomeEmailIsSent() {
        // Given
        when(userRepository.existsByEmail(testUser.getEmail())).thenReturn(false);
        when(userRepository.save(testUser)).thenReturn(testUser);
        
        // When
        userService.createUser(testUser);
        
        // Then
        verify(emailService).sendWelcomeEmail("test@example.com");
    }
    
    @Test
    public void givenValidUser_whenCreateUser_thenValidationIsPerformed() {
        // Given
        when(userRepository.existsByEmail(testUser.getEmail())).thenReturn(false);
        when(userRepository.save(testUser)).thenReturn(testUser);
        
        // When
        userService.createUser(testUser);
        
        // Then
        verify(validationService).validateUser(testUser);
    }
    
    @Test(expected = IllegalArgumentException.class)
    public void givenNullUser_whenCreateUser_thenThrowsIllegalArgumentException() {
        // When
        userService.createUser(null);
        
        // Then - exception expected
    }
    
    @Test(expected = DuplicateEmailException.class)
    public void givenExistingEmail_whenCreateUser_thenThrowsDuplicateEmailException() {
        // Given
        when(userRepository.existsByEmail(testUser.getEmail())).thenReturn(true);
        doNothing().when(validationService).validateUser(testUser);
        
        // When
        userService.createUser(testUser);
        
        // Then - exception expected
    }
    
    @Test
    public void givenDuplicateEmail_whenCreateUser_thenUserIsNotSaved() {
        // Given
        when(userRepository.existsByEmail(testUser.getEmail())).thenReturn(true);
        doNothing().when(validationService).validateUser(testUser);
        
        // When
        try {
            userService.createUser(testUser);
        } catch (DuplicateEmailException e) {
            // Expected exception
        }
        
        // Then
        verify(userRepository, never()).save(any(User.class));
        verify(emailService, never()).sendWelcomeEmail(anyString());
    }
    
    // ========================================
    // User Retrieval by ID Tests
    // ========================================
    
    @Test
    public void givenExistingUserId_whenGetUserById_thenReturnsUser() {
        // Given
        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));
        
        // When
        User result = userService.getUserById(1L);
        
        // Then
        assertThat(result).isNotNull();
        assertThat(result.getId()).isEqualTo(1L);
        assertThat(result.getEmail()).isEqualTo("test@example.com");
        verify(userRepository).findById(1L);
    }
    
    @Test(expected = UserNotFoundException.class)
    public void givenNonExistentUserId_whenGetUserById_thenThrowsUserNotFoundException() {
        // Given
        when(userRepository.findById(999L)).thenReturn(Optional.empty());
        
        // When
        userService.getUserById(999L);
        
        // Then - exception expected
    }
    
    @Test(expected = IllegalArgumentException.class)
    public void givenNullUserId_whenGetUserById_thenThrowsIllegalArgumentException() {
        // When
        userService.getUserById(null);
        
        // Then - exception expected
    }
    
    @Test
    public void givenUserIdZero_whenGetUserById_thenQueriesRepository() {
        // Given
        User userWithIdZero = new User(0L, "zero@example.com", "Zero User", true);
        when(userRepository.findById(0L)).thenReturn(Optional.of(userWithIdZero));
        
        // When
        User result = userService.getUserById(0L);
        
        // Then
        assertThat(result).isNotNull();
        assertThat(result.getId()).isEqualTo(0L);
        verify(userRepository).findById(0L);
    }
    
    // ========================================
    // User Retrieval by Email Tests
    // ========================================
    
    @Test
    public void givenExistingEmail_whenFindByEmail_thenReturnsUserInOptional() {
        // Given
        when(userRepository.findByEmail("test@example.com")).thenReturn(Optional.of(testUser));
        
        // When
        Optional<User> result = userService.findByEmail("test@example.com");
        
        // Then
        assertThat(result).isPresent();
        assertThat(result.get().getEmail()).isEqualTo("test@example.com");
        verify(userRepository).findByEmail("test@example.com");
    }
    
    @Test
    public void givenNonExistentEmail_whenFindByEmail_thenReturnsEmptyOptional() {
        // Given
        when(userRepository.findByEmail("nonexistent@example.com")).thenReturn(Optional.empty());
        
        // When
        Optional<User> result = userService.findByEmail("nonexistent@example.com");
        
        // Then
        assertThat(result).isEmpty();
        verify(userRepository).findByEmail("nonexistent@example.com");
    }
    
    @Test
    public void givenNullEmail_whenFindByEmail_thenReturnsEmptyOptional() {
        // When
        Optional<User> result = userService.findByEmail(null);
        
        // Then
        assertThat(result).isEmpty();
        verify(userRepository, never()).findByEmail(anyString());
    }
    
    @Test
    public void givenEmptyEmail_whenFindByEmail_thenReturnsEmptyOptional() {
        // When
        Optional<User> result = userService.findByEmail("");
        
        // Then
        assertThat(result).isEmpty();
        verify(userRepository, never()).findByEmail(anyString());
    }
    
    @Test
    public void givenWhitespaceEmail_whenFindByEmail_thenReturnsEmptyOptional() {
        // When
        Optional<User> result = userService.findByEmail("   ");
        
        // Then
        assertThat(result).isEmpty();
        verify(userRepository, never()).findByEmail(anyString());
    }
    
    // ========================================
    // Get All Active Users Tests
    // ========================================
    
    @Test
    public void givenMixedUsers_whenGetAllActiveUsers_thenReturnsOnlyActiveUsers() {
        // Given
        List<User> allUsers = Arrays.asList(activeUser, inactiveUser, testUser);
        when(userRepository.findAll()).thenReturn(allUsers);
        
        // When
        List<User> result = userService.getAllActiveUsers();
        
        // Then
        assertThat(result)
            .hasSize(2)
            .extracting(User::getEmail)
            .containsExactlyInAnyOrder("active@example.com", "test@example.com");
        assertThat(result)
            .allMatch(User::isActive);
    }
    
    @Test
    public void givenNoUsers_whenGetAllActiveUsers_thenReturnsEmptyList() {
        // Given
        when(userRepository.findAll()).thenReturn(Collections.emptyList());
        
        // When
        List<User> result = userService.getAllActiveUsers();
        
        // Then
        assertThat(result).isEmpty();
        verify(userRepository).findAll();
    }
    
    @Test
    public void givenOnlyInactiveUsers_whenGetAllActiveUsers_thenReturnsEmptyList() {
        // Given
        when(userRepository.findAll()).thenReturn(Collections.singletonList(inactiveUser));
        
        // When
        List<User> result = userService.getAllActiveUsers();
        
        // Then
        assertThat(result).isEmpty();
    }
    
    @Test
    public void givenOnlyActiveUsers_whenGetAllActiveUsers_thenReturnsAllUsers() {
        // Given
        List<User> activeUsers = Arrays.asList(activeUser, testUser);
        when(userRepository.findAll()).thenReturn(activeUsers);
        
        // When
        List<User> result = userService.getAllActiveUsers();
        
        // Then
        assertThat(result).hasSize(2);
        assertThat(result).containsExactlyInAnyOrderElementsOf(activeUsers);
    }
    
    // ========================================
    // User Update Tests
    // ========================================
    
    @Test
    public void givenValidUpdate_whenUpdateUser_thenUserIsUpdatedAndSaved() {
        // Given
        User updatedUser = new User(null, "updated@example.com", "Updated Name", true);
        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));
        when(userRepository.save(any(User.class))).thenReturn(testUser);
        
        // When
        User result = userService.updateUser(1L, updatedUser);
        
        // Then
        assertThat(result).isNotNull();
        verify(userRepository).findById(1L);
        verify(userRepository).save(testUser);
        assertThat(testUser.getName()).isEqualTo("Updated Name");
        assertThat(testUser.getEmail()).isEqualTo("updated@example.com");
    }
    
    @Test(expected = UserNotFoundException.class)
    public void givenNonExistentUserId_whenUpdateUser_thenThrowsUserNotFoundException() {
        // Given
        User updatedUser = new User(null, "updated@example.com", "Updated Name", true);
        when(userRepository.findById(999L)).thenReturn(Optional.empty());
        
        // When
        userService.updateUser(999L, updatedUser);
        
        // Then - exception expected
    }
    
    // ========================================
    // User Deletion Tests
    // ========================================
    
    @Test
    public void givenExistingUserId_whenDeleteUser_thenUserIsDeleted() {
        // Given
        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));
        doNothing().when(userRepository).delete(testUser);
        
        // When
        userService.deleteUser(1L);
        
        // Then
        verify(userRepository).delete(testUser);
    }
    
    @Test
    public void givenExistingUserId_whenDeleteUser_thenGoodbyeEmailIsSent() {
        // Given
        when(userRepository.findById(1L)).thenReturn(Optional.of(testUser));
        doNothing().when(userRepository).delete(testUser);
        
        // When
        userService.deleteUser(1L);
        
        // Then
        verify(emailService).sendGoodbyeEmail("test@example.com");
    }
    
    @Test(expected = UserNotFoundException.class)
    public void givenNonExistentUserId_whenDeleteUser_thenThrowsUserNotFoundException() {
        // Given
        when(userRepository.findById(999L)).thenReturn(Optional.empty());
        
        // When
        userService.deleteUser(999L);
        
        // Then - exception expected
    }
    
    @Test
    public void givenNonExistentUser_whenDeleteUser_thenNoEmailIsSent() {
        // Given
        when(userRepository.findById(999L)).thenReturn(Optional.empty());
        
        // When
        try {
            userService.deleteUser(999L);
        } catch (UserNotFoundException e) {
            // Expected exception
        }
        
        // Then
        verify(emailService, never()).sendGoodbyeEmail(anyString());
    }
    
    // ========================================
    // Count Users Tests
    // ========================================
    
    @Test
    public void givenMultipleUsers_whenCountUsers_thenReturnsCorrectCount() {
        // Given
        when(userRepository.count()).thenReturn(5L);
        
        // When
        long result = userService.countUsers();
        
        // Then
        assertThat(result).isEqualTo(5L);
        verify(userRepository).count();
    }
    
    @Test
    public void givenNoUsers_whenCountUsers_thenReturnsZero() {
        // Given
        when(userRepository.count()).thenReturn(0L);
        
        // When
        long result = userService.countUsers();
        
        // Then
        assertThat(result).isEqualTo(0L);
    }
}
